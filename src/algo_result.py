import pandas as pd
import numpy as np
from src.tools import sharpe, calmar_ratio


class AlgoResult:
    def __init__(self, X: pd.DataFrame, B: np.ndarray):
        self.X = X
        self.B = B
        self._recalculate()

    def _recalculate(self):
        r = (self.X - 1) * self.B
        self.asset_r = r + 1
        self.r = r.sum(axis=1) + 1

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
            'calmar_ratio': self.calmar_ratio
        }
