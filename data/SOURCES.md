# Data sources and attribution

The acquisition script downloads CSV observations from FRED's public graph endpoint.

| Local file | FRED series | Meaning | Original provider |
|---|---|---|---|
| `data/raw/SP500.csv` | `SP500` | Daily S&P 500 close | S&P Dow Jones Indices LLC |
| `data/raw/VIXCLS.csv` | `VIXCLS` | Daily CBOE Volatility Index close | Cboe |
| `data/raw/DGS10.csv` | `DGS10` | Daily 10-year Treasury constant-maturity yield | Federal Reserve Board |

Accessed programmatically on the date recorded in `data/raw/acquisition_metadata.json`.

Important limitations:

- `SP500` is a price index and does not include dividends.
- FRED provides ten years of daily history for the S&P 500 series.
- Missing observations occur on market holidays and are preserved in the raw files.
- The project does not redistribute third-party data through source control; raw downloads are reproducible from the documented URLs.
- Past performance does not predict future results. This project is educational and not investment advice.

