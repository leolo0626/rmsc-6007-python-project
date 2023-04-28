import pandas as pd
import numpy as np

from src.algo_base import AlgoBase
from src.tools import sharpe, calmar_ratio, to_rebalance


class AlgoResult:
    def __init__(self, X: pd.DataFrame, B: np.ndarray):
        self.X = X
        self.B = B
        self._fee = 0.0
        self._recalculate()

    def _recalculate(self):
        r = (self.X - 1) * self.B

        self.fees = self._to_rebalance().abs() * self.fee

        self.asset_r = r + 1
        self.asset_r -= self.fees

        self.r = r.sum(axis=1) + 1
        self.r -= self.fees.sum(axis=1)
        self.r = np.maximum(self.r, 1e-10)

    def _to_rebalance(self):
        return to_rebalance(self.B, self.X)

    @property
    def fee(self):
        return self._fee

    @fee.setter
    def fee(self, value: float):
        self._fee = value
        self._recalculate()


    @property
    def weights(self):
        return self.B

    @property
    def equity_curve(self):
        return self.r.cumprod()

    @property
    def total_wealth(self):
        return self.r.prod()

    @property
    def asset_equity(self):
        return self.X.cumprod()

    @property
    def equity_decomposed(self):
        return self.asset_r.cumprod()

    @property
    def annualized_return(self):
        return (self.r-1).mean() * 252

    @property
    def annualized_volatility(self):
        return (self.r-1).std() * np.sqrt(252)

    @property
    def sharpe_ratio(self):
        return sharpe(self.r - 1)

    @property
    def calmar_ratio(self):
        return calmar_ratio(self.r - 1)

    @property
    def max_drawdown(self):
        x = self.equity_curve
        return max(1 - x / x.cummax())

    @property
    def drawdown_curve(self):
        x = self.equity_curve
        return -(1 - x / x.cummax())

    def summary(self):
        return {
            'annualized_return': self.annualized_return,
            'annualized_volatility': self.annualized_volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'mdd': self.max_drawdown,
            'calmar_ratio': self.calmar_ratio,
            'final_wealth': self.total_wealth
        }


def get_algo_result(asset_prices, weights):
    price_relatives = AlgoBase.transform_price_data(asset_prices)
    weights = pd.DataFrame(weights[1:], index=price_relatives.index, columns=price_relatives.columns)
    algo_results = AlgoResult(price_relatives, weights)
    return algo_results