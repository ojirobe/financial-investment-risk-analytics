"""Execute selected SQL risk analyses and save evidence-backed outputs."""

import json
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "market_risk.db"
OUT = ROOT / "reports" / "sql_results"

QUERIES = {
    "annual_summary": """
        SELECT strftime('%Y', date) AS year,
               ROUND(100 * AVG(sp500_return), 4) AS average_daily_return_pct,
               ROUND(100 * AVG(sp500_vol_21d), 2) AS average_21d_volatility_pct,
               ROUND(AVG(vix), 2) AS average_vix
        FROM market_daily GROUP BY year ORDER BY year
    """,
    "worst_days": """
        SELECT date, ROUND(100 * sp500_return, 2) AS return_pct, ROUND(vix, 2) AS vix
        FROM market_daily ORDER BY sp500_return ASC LIMIT 10
    """,
    "risk_regimes": """
        SELECT CASE WHEN vix >= 30 THEN 'high_stress'
                    WHEN vix >= 20 THEN 'elevated' ELSE 'calm' END AS regime,
               COUNT(*) AS trading_days,
               ROUND(100 * AVG(sp500_return), 4) AS average_return_pct,
               ROUND(100 * AVG(ABS(sp500_return)), 4) AS average_absolute_return_pct
        FROM market_daily GROUP BY regime ORDER BY average_absolute_return_pct
    """,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as connection:
        for name, query in QUERIES.items():
            result = pd.read_sql_query(query, connection)
            result.to_csv(OUT / f"{name}.csv", index=False)
            print(f"\n{name}\n{result.to_string(index=False)}")


if __name__ == "__main__":
    main()

