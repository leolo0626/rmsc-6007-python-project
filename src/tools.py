import contextlib
import multiprocessing
import numpy as np
import pandas as pd
import scipy.optimize as optimize
import logging

from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam


@contextlib.contextmanager
def mp_pool(n_jobs):
    n_jobs = multiprocessing.cpu_count() if n_jobs == -1 else n_jobs
    print(f"# of worker: {n_jobs}")
    pool = multiprocessing.Pool(n_jobs)
    try:
        yield pool
    finally:
        pool.close()


def opt_weights(X: pd.DataFrame, **kwargs):
    '''
    X is prices in ratio
    '''
    b_tm1 = kwargs.pop('b_tm1')
    # x_0 = np.ones(X.shape[1]) / float(X.shape[1])
    x_0 = b_tm1
    opt_weight_param = kwargs.pop('opt_weight_param')
    if type(opt_weight_param) == TCAdjustedReturnOptWeightParam:
        fee = opt_weight_param.fee
        lda = opt_weight_param.lda

        # b_tm1 = kwargs.pop('b_tm1')

        def objective(b):
            return -np.sum(np.log(np.maximum(np.dot(X - 1, b) + 1, 0.0001))) + \
                   np.sum(np.maximum((b - b_tm1).abs() * lda, 1e-10))

        cons = {"type": "ineq", "fun": lambda b: 1 - sum(b) - np.sum(np.maximum((b - b_tm1).abs() * fee, 1e-10))}
    else:
        objective = lambda b: -np.sum(np.log(np.maximum(np.dot(X - 1, b) + 1, 0.0001)))
        # Equality constraint means that the constraint function result is to be zero
        cons = {"type": "eq", "fun": lambda b: 1 - sum(b)}

    while True:
        # problem optimization
        res = optimize.minimize(
            objective,  # objective function
            x_0,  # initial guess
            bounds=[(0.0, 1)] * len(x_0),
            constraints=cons,
            method="slsqp",  # Sequential Least SQuares Programming optimizer
            **kwargs,
        )

        # result can be out-of-bounds -> try it again
        EPS = 1e-7
        if (res.x < 0.0 - EPS).any() or (res.x > 1 + EPS).any():
            X = X + np.random.randn(1)[0] * 1e-5
            logging.debug("Optimal weights not found, trying again...")
            continue
        elif res.success:
            break
        else:
            if np.isnan(res.x).any():
                logging.warning("Solution does not exist, use zero weights.")
                res.x = np.zeros(X.shape[1])
            else:
                logging.warning("Converged, but not successfully.")
            break
    return res.x


def sharpe(r: pd.Series, rf_rate=0.0, freq=252):
    r = r - rf_rate
    mu = r.mean()
    sd = r.std()

    return mu / sd * np.sqrt(freq)


def calmar_ratio(r: pd.Series, freq=252):
    x = (1 + r).cumprod()
    mdd = max(1 - x / x.cummax())
    mu = r.mean()
    return mu / mdd * freq


def to_rebalance(B: np.ndarray, X: pd.DataFrame):
    """
    :param X: price relatives
    :param B: weight
    """
    E = (B * (X - 1)).sum(axis=1) + 1

    X = X.copy()

    hold_B = (B * X).div(E, axis=0)

    return B - hold_B.shift(1)

