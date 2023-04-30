from src.algo_base import AlgoBase
from src.algo_result import AlgoResult, get_algo_result
from src.data_provider.hsi_data_provider import HSIDataProvider
from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
from src.model.Instrument import HKEquityInstrument
from src.algo.CRP import CRP
from src.algo.CORN import CORN

import pandas as pd

from datetime import datetime
from src.data_provider.data_helper import count_na_in_dataframe
import matplotlib.pyplot as plt

from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam


def download_and_save_asset_prices():
    # read hsi constituents
    hsi_data_provider = HSIDataProvider()
    hist_hsi_constituents = hsi_data_provider.get_hist_hsi_constituents(save_csv=False)

    # select bear market from 2021-06-07 to 2021-09-05
    constituents_df = hist_hsi_constituents[hist_hsi_constituents['start_date'] == '2021-06-07']
    constituents = constituents_df.apply(lambda x: HKEquityInstrument(symbol=x['symbol'], location=x['location']),
                                         axis=1).to_list()
    # initialize yahoo finance data provider
    yf_provider = YahooFinanceDataProvider()

    # download hsi index price
    index_price = yf_provider.get_adj_close_of_stock('^HSI', '2021-06-07', '2021-09-05')
    index_price.to_csv('hsi_index_price.csv', index=True)

    # download asset price
    constituents_in_yf = [con.yahoo_finance_symbol for con in constituents]
    asset_price = yf_provider.get_multiple_stock_prices(constituents_in_yf, from_dt='2015-01-01', to_dt='2021-09-05')
    asset_price.to_csv('hsi_con_prices_20210607.csv', index=True)


if __name__ == "__main__":
    orig_asset_price = pd.read_csv('../data/HSI Index/hsi_con_prices_20210607.csv')
    orig_asset_price.set_index('Date', inplace=True)
    asset_price = orig_asset_price[orig_asset_price.index >= '2021-06-07']

    # CRP
    weights = CRP().run(asset_price)
    algo_result = get_algo_result(asset_price, weights, "CRP")
    algo_result.fee = 0.02 / 100
    print(algo_result.summary())
    # {'annualized_return': -0.26274719765320453, 'annualized_volatility': 0.15518998399928477,
    #  'sharpe_ratio': -1.6930680117501367, 'mdd': 0.11315066601696189, 'calmar_ratio': -2.3221003190013687,
    #  'final_wealth': 0.9346237485895997}

    # index price
    index_price = pd.read_csv('../data/HSI Index/hsi_index_price.csv')
    index_price.set_index('Date', inplace=True)
    index_result = get_algo_result(index_price, [1 for i in range(len(index_price))], "HSI")
    index_result.fee = 0
    print(index_result.summary())
    # {'annualized_return': -0.40591224034260037, 'annualized_volatility': 0.21547679664078853,
    #  'sharpe_ratio': -1.8837863132858712, 'mdd': 0.1515455665603621, 'calmar_ratio': -2.6784831094410237,
    #  'final_wealth': 0.8997720822192036}

    # CORN (Time consuming)
    # Need to run between different parameter
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=10, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(orig_asset_price)
    algo_result = get_algo_result(asset_price, corn_weights[-len(asset_price):], "CORN")
    algo_result.fee = 0.02 / 100
    print(algo_result.summary())
    # {'annualized_return': -0.17875497727374343, 'annualized_volatility': 0.15733456280545932,
    #  'sharpe_ratio': -1.1361456382268018, 'mdd': 0.10299288669357753, 'calmar_ratio': -1.7356050792669966,
    #  'final_wealth': 0.9540816941031289}
    # Todo: Optimize different parameters

    # Todo: Min Variance Portfolio
