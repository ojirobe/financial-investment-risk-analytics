-- Reproducible SQLite analyses for the prepared market_daily table.

-- Annual S&P 500 return and risk summary.
SELECT
    strftime('%Y', date) AS year,
    ROUND(100 * (MAX(sp500) / MIN(sp500) - 1), 2) AS range_based_price_change_pct,
    ROUND(100 * AVG(sp500_return), 4) AS average_daily_return_pct,
    ROUND(100 * AVG(sp500_vol_21d), 2) AS average_annualized_21d_volatility_pct,
    ROUND(AVG(vix), 2) AS average_vix
FROM market_daily
GROUP BY strftime('%Y', date)
ORDER BY year;

-- Worst S&P 500 daily returns.
SELECT date, ROUND(100 * sp500_return, 2) AS return_pct, ROUND(vix, 2) AS vix
FROM market_daily
ORDER BY sp500_return ASC
LIMIT 10;

-- Risk regime comparison.
SELECT
    CASE WHEN vix >= 30 THEN 'high_stress' WHEN vix >= 20 THEN 'elevated' ELSE 'calm' END AS regime,
    COUNT(*) AS trading_days,
    ROUND(100 * AVG(sp500_return), 4) AS average_sp500_return_pct,
    ROUND(100 * AVG(ABS(sp500_return)), 4) AS average_absolute_return_pct,
    ROUND(AVG(treasury_10y), 2) AS average_10y_yield_pct
FROM market_daily
GROUP BY regime
ORDER BY average_absolute_return_pct;

