"""Run the first reproducible market-risk analysis using only the standard library."""

from __future__ import annotations

import csv
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def read_fred_series(path: Path) -> Dict[str, float]:
    values: Dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        value_column = next(name for name in reader.fieldnames or [] if name != "observation_date")
        for row in reader:
            raw = row[value_column]
            if raw not in {"", "."}:
                values[row["observation_date"]] = float(raw)
    return values


def simple_returns(prices: Sequence[float]) -> List[float]:
    return [(current / previous) - 1.0 for previous, current in zip(prices, prices[1:])]


def annualized_volatility(returns: Sequence[float], periods: int = 252) -> float:
    return statistics.stdev(returns) * math.sqrt(periods)


def maximum_drawdown(prices: Sequence[float]) -> float:
    peak = prices[0]
    worst = 0.0
    for price in prices:
        peak = max(peak, price)
        worst = min(worst, price / peak - 1.0)
    return worst


def historical_var(returns: Sequence[float], confidence: float = 0.95) -> float:
    ordered = sorted(returns)
    index = max(0, math.ceil((1.0 - confidence) * len(ordered)) - 1)
    return -ordered[index]


def conditional_var(returns: Sequence[float], confidence: float = 0.95) -> float:
    threshold = -historical_var(returns, confidence)
    tail = [value for value in returns if value <= threshold]
    return -statistics.mean(tail)


def correlation(left: Sequence[float], right: Sequence[float]) -> float:
    mean_left = statistics.mean(left)
    mean_right = statistics.mean(right)
    numerator = sum((x - mean_left) * (y - mean_right) for x, y in zip(left, right))
    denominator = math.sqrt(
        sum((x - mean_left) ** 2 for x in left) * sum((y - mean_right) ** 2 for y in right)
    )
    return numerator / denominator


def build_aligned_rows() -> List[Tuple[str, float, float, float]]:
    sp500 = read_fred_series(RAW_DIR / "SP500.csv")
    vix = read_fred_series(RAW_DIR / "VIXCLS.csv")
    treasury = read_fred_series(RAW_DIR / "DGS10.csv")
    common_dates = sorted(set(sp500) & set(vix) & set(treasury))
    return [(date, sp500[date], vix[date], treasury[date]) for date in common_dates]


def main() -> None:
    rows = build_aligned_rows()
    if len(rows) < 252:
        raise RuntimeError("Expected at least one year of aligned daily observations.")

    dates = [row[0] for row in rows]
    prices = [row[1] for row in rows]
    vix_levels = [row[2] for row in rows]
    returns = simple_returns(prices)
    vix_changes = [current - previous for previous, current in zip(vix_levels, vix_levels[1:])]

    summary = {
        "analysis_generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "first_observation": dates[0],
        "last_observation": dates[-1],
        "aligned_observations": len(rows),
        "return_observations": len(returns),
        "cumulative_price_return_pct": round((prices[-1] / prices[0] - 1) * 100, 2),
        "annualized_volatility_pct": round(annualized_volatility(returns) * 100, 2),
        "maximum_drawdown_pct": round(maximum_drawdown(prices) * 100, 2),
        "historical_var_95_pct": round(historical_var(returns) * 100, 2),
        "conditional_var_95_pct": round(conditional_var(returns) * 100, 2),
        "return_vix_change_correlation": round(correlation(returns, vix_changes), 3),
        "latest_sp500_close": prices[-1],
        "latest_vix_close": vix_levels[-1],
        "latest_10y_treasury_yield_pct": rows[-1][3],
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with (PROCESSED_DIR / "aligned_market_data.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "sp500", "vix", "dgs10"])
        writer.writerows(rows)
    (PROCESSED_DIR / "risk_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print("First market-risk analysis")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

