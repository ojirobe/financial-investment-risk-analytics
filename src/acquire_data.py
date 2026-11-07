"""Download documented market-risk series from FRED without an API key."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
SERIES = {
    "SP500": "S&P 500 daily close (price index, dividends excluded)",
    "VIXCLS": "CBOE Volatility Index daily close",
    "DGS10": "10-year Treasury constant-maturity yield",
}


def download_series(series_id: str, destination: Path) -> int:
    url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id={series_id}&cosd=2016-01-01"
    )
    subprocess.run(
        [
            "curl",
            "-L",
            "--fail",
            "--silent",
            "--show-error",
            "--max-time",
            "45",
            "--retry",
            "2",
            "--output",
            str(destination),
            url,
        ],
        check=True,
    )
    return destination.stat().st_size


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    downloads = {}
    for series_id, description in SERIES.items():
        destination = RAW_DIR / f"{series_id}.csv"
        byte_count = download_series(series_id, destination)
        downloads[series_id] = {
            "description": description,
            "url": f"https://fred.stlouisfed.org/series/{series_id}",
            "file": str(destination.relative_to(ROOT)),
            "bytes": byte_count,
        }
        print(f"Downloaded {series_id}: {byte_count:,} bytes")

    metadata = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "transport": "FRED public graph CSV endpoint",
        "downloads": downloads,
    }
    (RAW_DIR / "acquisition_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

