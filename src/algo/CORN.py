from src.algo_base import AlgoBase
from src.tools import opt_weights
import numpy as np
import pandas as pd


class CORN(AlgoBase):
    def __init__(self, window_size: int, corr_threshold: float):
        self.window_size = window_size
        self.corr_threshold = corr_threshold
        super().__init__()

    def step(self, last_weight: np.ndarray, history: pd.DataFrame) -> np.ndarray:
        w = self.window_size
        corr_similar_set = set()
        asset_m = len(history.columns)
        t = len(history)
        b_tp1 = np.ones(asset_m) / asset_m

        if t <= w:
            return b_tp1

        price_seq_t = history.iloc[t - w: t].values.flatten()

        # Can use multiprocessing to speed up
        for i in range(w + 1, t + 1):
            if np.corrcoef(history.iloc[i - 1 - w: i - 1].values.flatten(), price_seq_t)[0, 1] >= self.corr_threshold:
                corr_similar_set.add(i - 1)
        if corr_similar_set:
            b_tp1 = self.optimize_weight(history.iloc[list(corr_similar_set), :])

        return b_tp1

    def optimize_weight(self, data: pd.DataFrame):
        return opt_weights(data)
