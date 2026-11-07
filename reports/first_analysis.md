# First executed market-risk analysis

Generated from the documented FRED downloads on 7 November 2026.

## Validation

- 2,495 dates had non-missing S&P 500, VIX, and 10-year Treasury observations.
- The aligned window ran from 2016-11-07 through 2026-11-05.
- 2,494 daily S&P 500 returns were calculated.
- Four automated risk-metric tests passed.

## Findings

The S&P 500 price index increased 245.00% across the aligned window. Annualized daily volatility was 18.19%, while the worst observed peak-to-trough decline was 33.92%.

Historical 95% one-day VaR was 1.69%. This is an empirical quantile, meaning roughly 5% of observed daily losses were worse than 1.69%. Conditional VaR was 2.79%, representing the average loss within that tail.

Daily S&P 500 returns had a -0.788 correlation with daily changes in the VIX. This is consistent with volatility tending to rise when equities fall, but correlation is not causation and the relationship may change over time.

## Latest aligned observation

- S&P 500 close: 7,353.73
- VIX close: 28.18
- 10-year Treasury yield: 4.84%

The latest aligned date was 2026-11-05. Values are historical observations, not live quotes.
