"""Construct and evaluate transparent long-only multi-asset portfolios."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "market_features.csv"
OUT = ROOT / "data" / "processed"
ASSETS = ["sp500", "nasdaq", "gold", "bonds"]
RETURN_COLUMNS = [f"{asset}_return" for asset in ASSETS]


def portfolio_statistics(weights: np.ndarray, mean_returns: pd.Series, covariance: pd.DataFrame, risk_free: float) -> tuple[float, float, float]:
    annual_return = float(weights @ mean_returns * 252)
    annual_volatility = float(np.sqrt(weights @ (covariance * 252) @ weights))
    sharpe = (annual_return - risk_free) / annual_volatility if annual_volatility else np.nan
    return annual_return, annual_volatility, sharpe


def optimize_portfolios(returns: pd.DataFrame, risk_free: float) -> dict[str, np.ndarray]:
    mean_returns = returns.mean()
    covariance = returns.cov()
    count = len(mean_returns)
    initial = np.repeat(1 / count, count)
    bounds = tuple((0.0, 1.0) for _ in range(count))
    constraints = ({"type": "eq", "fun": lambda weights: np.sum(weights) - 1.0},)

    minimum_volatility = minimize(
        lambda weights: portfolio_statistics(weights, mean_returns, covariance, risk_free)[1],
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    maximum_sharpe = minimize(
        lambda weights: -portfolio_statistics(weights, mean_returns, covariance, risk_free)[2],
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    if not minimum_volatility.success or not maximum_sharpe.success:
        raise RuntimeError("Portfolio optimization failed")
    return {
        "equal_weight": initial,
        "minimum_volatility": minimum_volatility.x,
        "maximum_sharpe": maximum_sharpe.x,
    }


def max_drawdown(series: pd.Series) -> float:
    wealth = (1 + series).cumprod()
    return float((wealth / wealth.cummax() - 1).min())


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["date"])
    returns = frame[RETURN_COLUMNS].dropna()
    latest_risk_free = float(frame["treasury_10y"].iloc[-1] / 100)
    portfolios = optimize_portfolios(returns, latest_risk_free)
    mean_returns, covariance = returns.mean(), returns.cov()
    rows = []
    cumulative = pd.DataFrame(index=frame.loc[returns.index, "date"])

    for name, weights in portfolios.items():
        portfolio_returns = returns.to_numpy() @ weights
        annual_return, annual_volatility, sharpe = portfolio_statistics(weights, mean_returns, covariance, latest_risk_free)
        loss_quantile = np.quantile(portfolio_returns, 0.05)
        rows.append({
            "portfolio": name,
            **{f"weight_{asset}": float(weight) for asset, weight in zip(ASSETS, weights)},
            "annual_return_pct": annual_return * 100,
            "annual_volatility_pct": annual_volatility * 100,
            "sharpe_ratio": sharpe,
            "maximum_drawdown_pct": max_drawdown(pd.Series(portfolio_returns)) * 100,
            "historical_var_95_pct": -loss_quantile * 100,
            "conditional_var_95_pct": -portfolio_returns[portfolio_returns <= loss_quantile].mean() * 100,
        })
        cumulative[name] = np.cumprod(1 + portfolio_returns)

    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "portfolio_summary.csv", index=False)
    cumulative.reset_index(names="date").to_csv(OUT / "portfolio_growth.csv", index=False)
    (ROOT / "reports" / "portfolio_results.json").write_text(summary.to_json(orient="records", indent=2) + "\n")
    print(summary.round(4).to_string(index=False))


if __name__ == "__main__":
    main()

