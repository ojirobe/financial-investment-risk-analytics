import numpy as np
import pandas as pd

from src.portfolio_analysis import optimize_portfolios
from src.train_model import make_dataset


def test_portfolio_weights_are_long_only_and_sum_to_one():
    rng = np.random.default_rng(42)
    returns = pd.DataFrame(rng.normal(0.0005, 0.01, size=(400, 4)), columns=["a", "b", "c", "d"])
    portfolios = optimize_portfolios(returns, risk_free=0.02)
    for weights in portfolios.values():
        assert np.isclose(weights.sum(), 1.0)
        assert (weights >= -1e-8).all()


def test_stress_threshold_uses_training_period_only():
    rows = 100
    frame = pd.DataFrame({feature: np.zeros(rows) for feature in [
        "sp500_return", "nasdaq_return", "gold_return", "bonds_return",
        "sp500_vol_21d", "nasdaq_vol_21d", "gold_vol_21d", "bonds_vol_21d",
        "vix", "vix_change", "treasury_10y",
    ]})
    frame.loc[1:79, "sp500_return"] = np.linspace(-0.01, 0.01, 79)
    frame.loc[80:, "sp500_return"] = 1.0
    _, _, threshold = make_dataset(frame, train_end=80)
    assert threshold < 0.02

