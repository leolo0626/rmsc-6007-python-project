import pandas as pd
import numpy as np
from typing import Optional


class AlgoBase:
    def __init__(self, min_history: Optional[int] = None):
        self.min_history = min_history or 0

    @staticmethod
    def transform_price_data(data: pd.DataFrame):
        transformed_data = data / data.shift(1)
        transformed_data.index = [i for i in range(len(data))]
        transformed_data.drop(index=transformed_data.index[0], axis=0, inplace=True)
        return transformed_data

    def init_step(self, assets_m) -> np.ndarray:
        return np.ones(assets_m) / assets_m

    def step(self, last_weight: np.ndarray, history: pd.DataFrame) -> np.ndarray:
        pass

    def run(self, historical_data: pd.DataFrame) -> np.ndarray:
        m = len(historical_data.columns)  # number of assets
        n = len(historical_data)  # backtest period includes first day
        prices_sequence = AlgoBase.transform_price_data(historical_data)
        # init weights
        weights = np.zeros((n, m))

        last_weight = self.init_step(m)

        for t in range(1, n):
            print(f"backtesting t={t}")
            weights[t] = last_weight

            if t < self.min_history:
                continue

            # predict for t+1
            history = prices_sequence.iloc[: int(t + 1)]
            last_weight = self.step(last_weight, history)

        return weights
