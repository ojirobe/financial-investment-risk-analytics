# Financial & Investment Risk Analytics

**Live dashboard:** [financial-investment-risk-analytics-ojirobe.streamlit.app](https://financial-investment-risk-analytics-ojirobe.streamlit.app/)

Project 3 of a five-project analytics portfolio. This repository implements a reproducible market-risk workflow with daily financial data, SQL, statistical tests, constrained portfolio optimization, leakage-safe modelling, an interactive dashboard, and automated tests.

> Historical and educational analysis only. Nothing in this repository is investment advice, a trading signal, or a recommendation to buy or sell any asset.

## Business questions

1. How large have historical volatility, drawdowns, VaR, and tail losses been?
2. How do returns behave during calm, elevated, and high-VIX regimes?
3. Do equity returns satisfy normality and stationarity assumptions?
4. How do equal-weight, minimum-volatility, and maximum-Sharpe portfolios compare?
5. Can information available today identify elevated next-day market-stress probability without temporal leakage?

## Data

Six daily series are downloaded from FRED with retrieval metadata:

- S&P 500 price index (`SP500`), S&P Dow Jones Indices LLC.
- Nasdaq Composite price index (`NASDAQCOM`), Nasdaq, Inc.
- PHLX Gold/Silver Sector Index (`NASDAQXAU`), Nasdaq, Inc.
- ICE BofA US Corporate Index Total Return Index Value (`BAMLCC0A0CMTRIV`), ICE Data Indices, LLC.
- CBOE Volatility Index (`VIXCLS`), Cboe.
- 10-year Treasury constant-maturity yield (`DGS10`), Federal Reserve Board.

The ten-year S&P 500 risk analysis contains 2,495 aligned observations from 7 November 2016 through 5 November 2026. The common multi-asset window contains 774 validated observations from 6 December 2023 through 6 November 2026 because FRED currently exposes roughly three years for the corporate-bond index. The S&P 500 and Nasdaq are price indices and exclude dividends.

See [data/SOURCES.md](data/SOURCES.md) for attribution and limitations.

## Ten-year S&P 500 risk results

| Metric | Result | Interpretation |
|---|---:|---|
| Cumulative price return | 245.00% | Price appreciation only; dividends excluded. |
| Annualized daily volatility | 18.19% | Daily dispersion scaled by 252 trading days. |
| Maximum drawdown | -33.92% | Largest observed peak-to-trough decline. |
| 95% historical one-day VaR | 1.69% | Roughly 5% of observed days lost more than this. |
| 95% historical one-day CVaR | 2.79% | Average loss beyond the VaR threshold. |
| Return/VIX-change correlation | -0.788 | Equity declines were associated with rising implied volatility. |

## Statistical evidence

- Jarque–Bera rejects normal daily returns (`p < 0.001`), supporting empirical tail-risk measures.
- Levene's test finds different variance between calm and high-stress regimes (`p ≈ 1.15e-33`).
- The calm/high-stress mean-return difference is not significant at 5% (`p = 0.357`); only 15 high-stress observations were available.
- Augmented Dickey–Fuller results are consistent with non-stationary price levels (`p = 0.615`) and stationary returns (`p < 0.001`).

## Portfolio findings

The optimization is long-only, fully invested, and in-sample. The latest 10-year Treasury yield is the illustrative risk-free rate.

| Portfolio | Annual return | Annual volatility | Sharpe | Maximum drawdown | 95% VaR |
|---|---:|---:|---:|---:|---:|
| Equal weight | 20.87% | 15.67% | 1.02 | -12.37% | 1.54% |
| Minimum volatility | 4.70% | 4.71% | -0.03 | -4.11% | 0.47% |
| Maximum Sharpe | 26.42% | 20.11% | 1.07 | -15.43% | 2.04% |

The weights are sensitive to the selected history and exclude fees, taxes, slippage, and implementation constraints. They are demonstrations, not allocations.

## Predictive model

The model predicts whether the next day's absolute S&P 500 return exceeds a stress threshold learned only from the training period. It uses a chronological 80/20 split, five sequential calibration folds, median imputation, standardization, and logistic regression.

| Test metric | Result |
|---|---:|
| ROC AUC | 0.680 |
| Average precision / PR AUC | 0.203 |
| Event prevalence | 0.097 |
| Balanced accuracy | 0.523 |
| Brier score | 0.0877 |
| Prevalence baseline Brier | 0.0879 |

The model shows modest ranking information and only marginal calibration improvement. It is not strong enough to justify trading or capital-allocation decisions.

## Project structure

```text
app.py                      Streamlit Cloud entry point
dashboards/app.py           Interactive dashboard
data/SOURCES.md             Provenance and limitations
src/acquire_data.py         Reproducible FRED downloads
src/prepare_data.py         Validation, alignment, features, SQLite
src/first_analysis.py       Ten-year S&P 500 risk metrics
src/run_sql_analysis.py     Executed SQL reporting
src/statistical_analysis.py Hypothesis and stationarity tests
src/portfolio_analysis.py   Long-only portfolio optimization
src/train_model.py          Leakage-safe stress classifier
sql/risk_analysis.sql       Reusable SQL queries
tests/                      Metric, leakage, portfolio, and dashboard tests
reports/                    Executed aggregate results and case study
```

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python src/acquire_data.py
python src/prepare_data.py
python src/first_analysis.py
python src/run_sql_analysis.py
python src/statistical_analysis.py
python src/portfolio_analysis.py
python src/train_model.py
pytest -q
streamlit run app.py
```

Raw and row-level processed market data are excluded from Git. The dashboard rebuilds them from the documented sources when they are absent.

## Deployment

The repository includes `runtime.txt` for Python 3.12 and a root `app.py` for Streamlit Community Cloud. Deploy branch `main` with `app.py` as the entry point. No secrets are required.

## Responsible limitations

- Historical relationships may break in future regimes.
- Index levels are not directly investable portfolios.
- Price indices may exclude distributions; results differ from total returns.
- FRED series can be revised, shortened, delayed, or discontinued.
- Optimization estimates are in-sample and sensitive to short histories.
- VaR does not describe losses beyond its threshold; CVaR is included for that reason.
- The classifier is a methodological demonstration and must not be used as a trading system.

## License

Code is available under the MIT License. Third-party data remain subject to their providers' terms and are not covered by the code license.

