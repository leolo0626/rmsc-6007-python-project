from typing import List

import numpy as np
import pandas as pd

from src.algo.CORN import CORN
from src.algo_runner import AlgoRunnerReq, AlgoRunner
from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam

from src.tools import mp_pool


def get_algo_runner_req_corn():
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    #
    rho = np.arange(0.1, 1, 0.2)
    windows = np.arange(10, 65, 10)
    unique_combinations = []
    for i in range(len(rho)):
        for j in range(len(windows)):
            req_param = {
                "window_size": windows[j],
                "corr_threshold": round(rho[i], 2),
                "opt_weights_param": opt_weight_param
            }
            unique_combinations.append(
                AlgoRunnerReq(
                    params=req_param,
                    algo_class=CORN
                )
            )
    return unique_combinations


def algo_runner_mp_corn(asset_price: pd.DataFrame, reqs: List[AlgoRunnerReq], save_path: str):
    algo_runner = AlgoRunner(
        asset_price=asset_price,
        abs_parent_path=None,
        save_path=save_path,
    )
    with mp_pool(-1) as p:
        results = p.map(algo_runner.run_and_save, reqs)


if __name__ == "__main__":
    algo_reqs = get_algo_runner_req_corn()
    algo_runner = AlgoRunner(
        asset_price=None,
        abs_parent_path=None,
        save_path='data/HSI Index/Bull',
    )

    print(algo_runner.save_path)
