import unittest

from src.first_analysis import (
    annualized_volatility,
    conditional_var,
    historical_var,
    maximum_drawdown,
    simple_returns,
)


class RiskMetricTests(unittest.TestCase):
    def test_simple_returns(self):
        actual = simple_returns([100.0, 110.0, 99.0])
        self.assertAlmostEqual(actual[0], 0.1)
        self.assertAlmostEqual(actual[1], -0.1)

    def test_maximum_drawdown(self):
        self.assertAlmostEqual(maximum_drawdown([100.0, 120.0, 90.0, 110.0]), -0.25)

    def test_var_and_cvar_are_positive_loss_magnitudes(self):
        returns = [-0.10, -0.05, -0.02, 0.01, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
        self.assertAlmostEqual(historical_var(returns, 0.90), 0.10)
        self.assertAlmostEqual(conditional_var(returns, 0.90), 0.10)

    def test_volatility_is_zero_only_for_constant_returns(self):
        self.assertAlmostEqual(annualized_volatility([0.01, 0.01, 0.01]), 0.0)


if __name__ == "__main__":
    unittest.main()

