import numpy as np
import pandas as pd

from src.algo_base import AlgoBase


class CRP(AlgoBase):
    def __init__(self):
        super().__init__()

    def step(self, last_weight: np.ndarray, history: pd.DataFrame):
        asset_m = len(history.columns)
        return np.ones(asset_m) / asset_m