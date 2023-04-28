from src.algo_base import AlgoBase
from src.algo_result import AlgoResult, get_algo_result
from src.data_provider.hsi_data_provider import get_hist_hsi_constituents
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
    hist_hsi_constituents = get_hist_hsi_constituents(save_csv=False)

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
    # constituents_in_yf = [con.yahoo_finance_symbol for con in constituents]
    # asset_price = yf_provider.get_multiple_stock_prices(constituents_in_yf, from_dt='2015-01-01', to_dt='2021-09-05')
    # asset_price.to_csv('hsi_con_prices_20210607.csv', index=True)


if __name__ == "__main__":

    orig_asset_price = pd.read_csv('../data/HSI Index/hsi_con_prices_20210607.csv')
    orig_asset_price.set_index('Date', inplace=True)
    asset_price = orig_asset_price[orig_asset_price.index >= '2021-06-07']

    # # CRP
    # weights = CRP().run(asset_price)
    # algo_result = get_algo_result(asset_price, weights)
    # algo_result.fee = 0.02 / 100
    # print(algo_result.summary())
    #
    # # index price
    # index_price = pd.read_csv('../data/HSI Index/hsi_index_price.csv')
    # index_price.set_index('Date', inplace=True)
    # index_result = get_algo_result(index_price, [1 for i in range(len(index_price))])
    # index_result.fee = 0
    # print(index_result.summary())

    # CORN
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=30, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(orig_asset_price)
    print(corn_weights)

