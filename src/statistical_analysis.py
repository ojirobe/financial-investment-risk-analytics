"""Run distributional and market-stress hypothesis tests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "market_features.csv"
OUTPUT = ROOT / "reports" / "statistical_tests.json"


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["date"])
    returns = frame["sp500_return"].dropna()
    calm = frame.loc[frame["vix"] < 20, "sp500_return"].dropna()
    stress = frame.loc[frame["vix"] >= 30, "sp500_return"].dropna()

    jb = stats.jarque_bera(returns)
    mean_test = stats.ttest_ind(stress, calm, equal_var=False)
    variance_test = stats.levene(stress, calm, center="median")
    adf_price = adfuller(frame["sp500"], autolag="AIC")
    adf_return = adfuller(returns, autolag="AIC")

    results = {
        "jarque_bera_normality": {
            "statistic": float(jb.statistic),
            "p_value": float(jb.pvalue),
            "interpretation": "Reject normal daily returns" if jb.pvalue < 0.05 else "Insufficient evidence against normality",
        },
        "stress_vs_calm_mean_return_welch_ttest": {
            "calm_days": int(len(calm)),
            "stress_days": int(len(stress)),
            "calm_mean_pct": float(calm.mean() * 100),
            "stress_mean_pct": float(stress.mean() * 100),
            "statistic": float(mean_test.statistic),
            "p_value": float(mean_test.pvalue),
        },
        "stress_vs_calm_variance_levene": {
            "statistic": float(variance_test.statistic),
            "p_value": float(variance_test.pvalue),
            "interpretation": "Volatility differs by regime" if variance_test.pvalue < 0.05 else "No significant variance difference",
        },
        "augmented_dickey_fuller": {
            "price_statistic": float(adf_price[0]),
            "price_p_value": float(adf_price[1]),
            "return_statistic": float(adf_return[0]),
            "return_p_value": float(adf_return[1]),
            "interpretation": "Prices are non-stationary; returns are stationary" if adf_price[1] >= 0.05 and adf_return[1] < 0.05 else "Review stationarity results",
        },
    }
    OUTPUT.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

