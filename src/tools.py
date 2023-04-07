import numpy as np
import pandas as pd
import scipy.optimize as optimize
import logging


def opt_weights(X: pd.DataFrame, **kwargs):
    '''
    X is prices in ratio
    '''
    objective = lambda b: -np.sum(np.log(np.maximum(np.dot(X - 1, b) + 1, 0.0001)))
    # Equality constraint means that the constraint function result is to be zero
    cons = {"type": "eq", "fun": lambda b: 1 - sum(b)}
    x_0 = np.ones(X.shape[1]) / float(X.shape[1])

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
