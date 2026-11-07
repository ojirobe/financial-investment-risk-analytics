"""Validate, align, and enrich the downloaded FRED market series."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DB_PATH = PROCESSED / "market_risk.db"

SERIES_COLUMNS = {
    "SP500": "sp500",
    "NASDAQCOM": "nasdaq",
    "NASDAQXAU": "gold",
    "BAMLCC0A0CMTRIV": "bonds",
    "VIXCLS": "vix",
    "DGS10": "treasury_10y",
}
ASSETS = ["sp500", "nasdaq", "gold", "bonds"]


def load_series(series_id: str, output_name: str) -> pd.DataFrame:
    frame = pd.read_csv(RAW / f"{series_id}.csv", na_values=".")
    frame.columns = ["date", output_name]
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame[output_name] = pd.to_numeric(frame[output_name], errors="coerce")
    if frame["date"].duplicated().any():
        raise ValueError(f"Duplicate dates found in {series_id}")
    if (frame[output_name].dropna() <= 0).any():
        raise ValueError(f"Non-positive values found in {series_id}")
    return frame


def build_market_data() -> tuple[pd.DataFrame, dict]:
    frames = [load_series(series, name) for series, name in SERIES_COLUMNS.items()]
    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="date", how="outer", validate="one_to_one")
    merged = merged.sort_values("date").set_index("date")

    raw_missing = merged.isna().sum().to_dict()
    # Forward-fill at most three calendar rows so weekends/short holidays do not
    # become artificial gaps; longer source gaps remain missing.
    aligned = merged.ffill(limit=3).dropna().copy()
    for asset in ASSETS:
        aligned[f"{asset}_return"] = aligned[asset].pct_change()
        aligned[f"{asset}_vol_21d"] = aligned[f"{asset}_return"].rolling(21).std() * np.sqrt(252)
    aligned["vix_change"] = aligned["vix"].diff()
    aligned["sp500_drawdown"] = aligned["sp500"] / aligned["sp500"].cummax() - 1
    aligned = aligned.dropna().reset_index()

    quality = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_rows": int(len(merged)),
        "processed_rows": int(len(aligned)),
        "first_date": aligned["date"].min().date().isoformat(),
        "last_date": aligned["date"].max().date().isoformat(),
        "duplicate_dates": int(aligned["date"].duplicated().sum()),
        "remaining_missing_values": int(aligned.isna().sum().sum()),
        "raw_missing_by_series": {key: int(value) for key, value in raw_missing.items()},
    }
    return aligned, quality


def write_outputs(frame: pd.DataFrame, quality: dict) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PROCESSED / "market_features.csv", index=False)
    (PROCESSED / "data_quality.json").write_text(json.dumps(quality, indent=2) + "\n")
    with sqlite3.connect(DB_PATH) as connection:
        frame.to_sql("market_daily", connection, if_exists="replace", index=False)
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_market_daily_date ON market_daily(date)")


def main() -> None:
    frame, quality = build_market_data()
    write_outputs(frame, quality)
    print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    main()

