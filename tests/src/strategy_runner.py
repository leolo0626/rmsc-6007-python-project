import pytest
import pandas as pd
import random
import numpy as np
from itertools import product
from src.algo.CORN import CORN
from src.algo.CRP import CRP
from multiprocessing import Pool

from src.data_provider.data_helper import count_na_in_dataframe

exempt_list = ['META', 'TSLA', 'PYPL', 'MRNA', 'CHTR', 'ZM', 'NXPI', 'DOCU', 'JD', 'KHC', 'TEAM', 'WDAY', 'XLNX',
               'PTON', 'PDD', 'OKTA', 'CDW', 'MXIM', 'CERN', 'SPLK', 'FOX']

selections = ['DXCM', 'MTCH', 'ADBE', 'BIIB', 'TXN', 'PCAR', 'FAST', 'MSFT', 'GILD', 'ADI']


def get_nasdaq_components_prices(subset=None):
    nasdaq100 = pd.read_csv('../../src/data/nasdaq100.csv', index_col=0)
    if subset is None:
        return nasdaq100
    return nasdaq100[subset]


# Todo: Need a data processing tools to fill na case

# def execute_function(args):
#     print(f'=========start {args}=========')
#     nasdaq100 = pd.read_csv('../../src/data/nasdaq100.csv', index_col=0)
#     nasdaq10 = nasdaq100[selections]
#     result = CORN(*args).run(nasdaq10)
#     result_df = pd.DataFrame(result)
#     result_df.to_csv(f'result_nasdaq10_corn_{args[0]:.2%}_{args[1]:.2%}.csv')
#     print(f'==========completed {args} ======')
#     return True

if __name__ == "__main__":
    # rho = np.arange(0.1, 1, 0.2)
    # windows = np.arange(10, 65, 10)
    # unique_combinations = []
    # for i in range(len(rho)):
    #     for j in range(len(windows)):
    #         unique_combinations.append((windows[j], rho[i]))
    #
    # with Pool(5) as p:
    #     results = p.map(execute_function, unique_combinations)
    historical_data = get_nasdaq_components_prices(selections)
    results = CRP().run(historical_data)
    result_df = pd.DataFrame(results)
    result_df.to_csv(f'result_nasdaq10_crp.csv')
