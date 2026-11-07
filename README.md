# Financial & Investment Risk Analytics

Project 3 of a five-project analytics portfolio. This project builds a reproducible market-risk workflow using daily financial data, SQL analysis, statistical testing, leakage-safe modelling, an interactive dashboard, and automated tests.

## Current stage

- Project structure created.
- FRED data-acquisition script prepared for the S&P 500, VIX, and 10-year Treasury yield.
- First risk analysis computes daily returns, annualized volatility, maximum drawdown, historical Value at Risk (VaR), Conditional VaR, and return/VIX-change correlation.

## First executed results

The initial run aligned 2,495 daily observations from 7 November 2016 through 5 November 2026:

| Metric | Result | Interpretation |
|---|---:|---|
| S&P 500 cumulative price return | 245.00% | Price appreciation only; dividends are excluded. |
| Annualized daily volatility | 18.19% | Historical dispersion scaled by 252 trading days. |
| Maximum drawdown | -33.92% | Largest peak-to-trough decline in the window. |
| 95% historical one-day VaR | 1.69% | About 5% of observed days lost more than this threshold. |
| 95% historical one-day Conditional VaR | 2.79% | Average loss among observations beyond the VaR threshold. |
| Return/VIX-change correlation | -0.788 | Equity declines were strongly associated with increases in implied volatility. |

These are descriptive historical estimates, not forecasts or investment recommendations. Results can change when the data window is refreshed.

## Data sources

- S&P Dow Jones Indices LLC, **S&P 500 [SP500]**, retrieved from FRED, Federal Reserve Bank of St. Louis: https://fred.stlouisfed.org/series/SP500
- Cboe, **CBOE Volatility Index: VIX [VIXCLS]**, retrieved from FRED: https://fred.stlouisfed.org/series/VIXCLS
- Board of Governors of the Federal Reserve System, **Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity [DGS10]**, retrieved from FRED: https://fred.stlouisfed.org/series/DGS10

The S&P 500 series is a price index and excludes dividends. Results are historical and educational, not investment advice.

## Reproduce the first analysis

```bash
python3 src/acquire_data.py
python3 src/first_analysis.py
python3 -m unittest discover -s tests -v
```

