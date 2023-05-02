import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.algo_result import get_algo_result
from src.utils.str_utils import extract_date_str

if __name__ == "__main__":
    asset_subset = ['DXCM', 'MTCH', 'ADBE', 'BIIB', 'TXN', 'PCAR', 'FAST', 'MSFT', 'GILD', 'ADI']
    algo_weight = pd.read_csv('../data/nasdaq/nasdaq10_corn_10/result_nasdaq10_corn_10_0.5.csv', index_col=0)
    # algo_weight = pd.read_csv('../data/nasdaq/nasdaq10_cornTC_10/result_nasdaq10TC_corn_10_0.5.csv', index_col=0)
    asset_price = pd.read_csv('../data/nasdaq100.csv', index_col=0)
    asset_price.index = [extract_date_str(idx) for idx in asset_price.index]
    asset_price.index = pd.to_datetime(asset_price.index, format='%Y-%m-%d')
    subset_asset_price = asset_price[asset_subset]
    algo_result = get_algo_result(subset_asset_price, algo_weight.to_numpy(), "CORN")
    result = []
    for tc in np.arange(0.01, 1, 0.01):
        algo_result.fee = tc / 100
        result.append({
           "tc_pct": tc/100,
           "annualized_return": round(algo_result.summary()['annualized_return'] * 100, 2)
        })


    result_df = pd.DataFrame(result)
    print(result_df.tail())
    sns.lineplot(data=result_df, x="tc_pct", y="annualized_return")
    plt.show()



