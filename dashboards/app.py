"""Interactive financial and investment risk dashboard."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def ensure_outputs() -> None:
    required = [
        PROCESSED / "market_features.csv",
        PROCESSED / "portfolio_summary.csv",
        ROOT / "reports" / "model_metrics.json",
    ]
    if all(path.exists() for path in required):
        return
    scripts = [
        "src/acquire_data.py", "src/prepare_data.py", "src/first_analysis.py",
        "src/run_sql_analysis.py", "src/statistical_analysis.py",
        "src/portfolio_analysis.py", "src/train_model.py",
    ]
    with st.spinner("Preparing the documented FRED data and analytics outputs..."):
        for script in scripts:
            subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)


@st.cache_data
def load_outputs():
    market = pd.read_csv(PROCESSED / "market_features.csv", parse_dates=["date"])
    portfolios = pd.read_csv(PROCESSED / "portfolio_summary.csv")
    growth = pd.read_csv(PROCESSED / "portfolio_growth.csv", parse_dates=["date"])
    predictions = pd.read_csv(PROCESSED / "model_predictions.csv", parse_dates=["date"])
    model_metrics = json.loads((ROOT / "reports" / "model_metrics.json").read_text())
    tests = json.loads((ROOT / "reports" / "statistical_tests.json").read_text())
    return market, portfolios, growth, predictions, model_metrics, tests


st.set_page_config(page_title="Financial Risk Analytics", page_icon="📉", layout="wide")
ensure_outputs()
market, portfolios, growth, predictions, model_metrics, statistical_tests = load_outputs()

st.title("Financial & Investment Risk Analytics")
st.caption("Historical multi-asset risk analysis using documented FRED data. Educational only—not investment advice.")

with st.sidebar:
    st.header("Analysis controls")
    date_range = st.date_input(
        "Date range",
        value=(market["date"].min().date(), market["date"].max().date()),
        min_value=market["date"].min().date(),
        max_value=market["date"].max().date(),
    )
    asset_label = st.selectbox("Primary asset", ["S&P 500", "Nasdaq", "Gold/Silver equities", "Corporate bonds"])
    st.markdown("**Sources:** FRED series SP500, NASDAQCOM, NASDAQXAU, BAMLCC0A0CMTRIV, VIXCLS, and DGS10.")
    st.caption("Price/index series do not represent investable total returns and may exclude dividends, fees, and transaction costs.")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start = end = pd.Timestamp(date_range)
filtered = market.loc[market["date"].between(start, end)].copy()
if len(filtered) < 30:
    st.error("Choose a range containing at least 30 aligned observations.")
    st.stop()

asset_map = {"S&P 500": "sp500", "Nasdaq": "nasdaq", "Gold/Silver equities": "gold", "Corporate bonds": "bonds"}
asset = asset_map[asset_label]
returns = filtered[f"{asset}_return"].dropna()
wealth = (1 + returns).cumprod()
drawdown = wealth / wealth.cummax() - 1
var_95 = -returns.quantile(0.05)
cvar_95 = -returns[returns <= returns.quantile(0.05)].mean()

metrics = st.columns(5)
metrics[0].metric("Observations", f"{len(filtered):,}")
metrics[1].metric("Price change", f"{(filtered[asset].iloc[-1] / filtered[asset].iloc[0] - 1) * 100:.1f}%")
metrics[2].metric("Annualized volatility", f"{returns.std() * np.sqrt(252) * 100:.1f}%")
metrics[3].metric("Maximum drawdown", f"{drawdown.min() * 100:.1f}%")
metrics[4].metric("95% daily VaR / CVaR", f"{var_95 * 100:.2f}% / {cvar_95 * 100:.2f}%")

overview, regimes, portfolio_tab, model_tab, methodology = st.tabs([
    "Market overview", "Risk regimes", "Portfolio laboratory", "Stress model", "Data & methodology"
])

with overview:
    normalized = filtered.set_index("date")[["sp500", "nasdaq", "gold", "bonds"]].rename(columns={"gold": "gold_silver_equities", "bonds": "corporate_bonds"})
    normalized = normalized / normalized.iloc[0] * 100
    fig = px.line(normalized, labels={"value": "Indexed value (start = 100)", "variable": "Asset"}, title="Normalized asset-price paths")
    st.plotly_chart(fig, width="stretch")
    left, right = st.columns(2)
    with left:
        fig = px.line(filtered, x="date", y="vix", title="VIX market-stress indicator")
        fig.add_hline(y=20, line_dash="dot", line_color="orange")
        fig.add_hline(y=30, line_dash="dot", line_color="red")
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.line(filtered, x="date", y="treasury_10y", title="10-year Treasury yield", labels={"treasury_10y": "Yield (%)"})
        st.plotly_chart(fig, width="stretch")

with regimes:
    regime_frame = filtered.assign(
        regime=pd.cut(filtered["vix"], bins=[0, 20, 30, np.inf], labels=["Calm (<20)", "Elevated (20–30)", "High stress (≥30)"])
    )
    summary = regime_frame.groupby("regime", observed=False)["sp500_return"].agg(["count", "mean", "std"]).reset_index()
    summary["mean_return_pct"] = summary["mean"] * 100
    summary["annualized_volatility_pct"] = summary["std"] * np.sqrt(252) * 100
    st.dataframe(summary[["regime", "count", "mean_return_pct", "annualized_volatility_pct"]], hide_index=True, width="stretch")
    fig = px.box(regime_frame, x="regime", y="sp500_return", points=False, labels={"sp500_return": "Daily S&P 500 return", "regime": "VIX regime"})
    st.plotly_chart(fig, width="stretch")
    levene = statistical_tests["stress_vs_calm_variance_levene"]
    st.info(f"Levene variance test p-value: {levene['p_value']:.3g}. {levene['interpretation']}.")

with portfolio_tab:
    display = portfolios.copy()
    for column in [name for name in display if name.endswith("_pct")]:
        display[column] = display[column].round(2)
    st.dataframe(display, hide_index=True, width="stretch")
    fig = px.scatter(
        portfolios, x="annual_volatility_pct", y="annual_return_pct", color="portfolio",
        hover_data=["sharpe_ratio", "maximum_drawdown_pct", "historical_var_95_pct"],
        labels={"annual_volatility_pct": "Annualized volatility (%)", "annual_return_pct": "Annualized historical return (%)"},
        title="Historical risk-return comparison",
    )
    st.plotly_chart(fig, width="stretch")
    st.plotly_chart(px.line(growth, x="date", y=["equal_weight", "minimum_volatility", "maximum_sharpe"], title="Growth of one historical unit"), width="stretch")
    st.warning("Optimized weights are in-sample illustrations and can be unstable. They exclude costs, taxes, slippage, and dividends and are not portfolio recommendations.")

with model_tab:
    a, b, c, d = st.columns(4)
    a.metric("ROC AUC", f"{model_metrics['roc_auc']:.3f}")
    b.metric("PR AUC", f"{model_metrics['pr_auc']:.3f}")
    c.metric("Balanced accuracy", f"{model_metrics['balanced_accuracy']:.3f}")
    d.metric("Brier score", f"{model_metrics['brier_score']:.3f}")
    st.plotly_chart(px.line(predictions, x="date", y="predicted_probability", title="Out-of-sample next-day stress probability"), width="stretch")
    st.markdown(
        f"The model uses a chronological split: **{model_metrics['training_rows']:,} training rows** ending "
        f"{model_metrics['training_end_date']} and **{model_metrics['test_rows']:,} later test rows** beginning "
        f"{model_metrics['test_start_date']}. The stress threshold ({model_metrics['stress_threshold_abs_return_pct']:.2f}% absolute return) "
        "was learned from the training period only."
    )
    st.warning("This classifier is an educational risk-monitoring demonstration, not a trading signal.")

with methodology:
    st.subheader("Reproducibility and responsible interpretation")
    st.markdown(
        """
- Raw series are downloaded directly from documented FRED endpoints. The `gold` analysis column represents the PHLX Gold/Silver Sector Index, not bullion.
- Missing values are forward-filled for no more than three rows; longer gaps are excluded.
- VaR is the empirical 5th-percentile loss. CVaR is the average loss beyond that threshold.
- Portfolio optimization is long-only and fully invested; historical estimates are in-sample.
- The predictive model uses a chronological 80/20 split, lag-available features, and a training-only target threshold.
- S&P 500 and Nasdaq are price indices; results do not include dividends, fees, taxes, or implementation costs.
- Historical associations are not causal claims and do not guarantee future outcomes.
        """
    )
    st.download_button("Download filtered market data", filtered.to_csv(index=False), "filtered_market_data.csv", "text/csv")

