import pandas as pd
import numpy as np
from src.tools import sharpe

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
    def sharpe_ratio(self):
        return sharpe(self.r-1)


