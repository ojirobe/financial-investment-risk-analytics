# Case study: Financial & Investment Risk Analytics

## Situation

Investment dashboards often emphasize returns while hiding tail risk, regime dependence, non-normality, and modelling limitations. This project connects source data to decisions without presenting historical optimization as advice.

## Task

Build a reproducible system that validates daily market series, measures downside risk, compares volatility regimes, demonstrates constrained diversification, and evaluates next-day stress predictability under a chronological test.

## Actions

1. Downloaded six documented FRED series with retrieval metadata.
2. Validated dates, types, positivity, duplicates, gaps, and the common window.
3. Limited forward filling to three rows and excluded longer missing periods.
4. Created SQLite analyses for annual summaries, worst days, and risk regimes.
5. Tested normality, variance differences, mean differences, and stationarity.
6. Estimated historical VaR, CVaR, volatility, and drawdowns.
7. Solved long-only minimum-volatility and maximum-Sharpe problems alongside an equal-weight benchmark.
8. Built a chronological calibrated classifier using a training-only target threshold.
9. Added an interactive dashboard and automated metric, leakage, portfolio, and UI checks.

## Results

- The ten-year S&P 500 price-index window had 18.19% annualized volatility and a -33.92% maximum drawdown.
- Historical one-day 95% VaR was 1.69%; tail losses averaged 2.79% beyond that threshold.
- VIX changes and S&P 500 returns had a -0.788 correlation.
- High-stress days had materially greater variance than calm days, while their mean difference was not significant with only 15 high-stress observations.
- The minimum-volatility portfolio reduced historical drawdown to -4.11% but had a slightly negative Sharpe ratio against the latest 10-year yield.
- The stress classifier achieved ROC AUC 0.680 and average precision 0.203, with only marginal Brier-score improvement over prevalence.

## Decision implications

- Tail-risk metrics should accompany volatility because returns are non-normal.
- Risk limits should account for regimes; calm-period estimates understate stressed dispersion.
- Optimized allocations require robust out-of-sample and transaction-cost analysis before practical use.
- The model is a methodological demonstration, not an operational trading signal.

