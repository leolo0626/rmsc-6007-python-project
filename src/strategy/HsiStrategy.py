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
from src.strategy.strategy_helper import get_algo_runner_req_corn, algo_runner_mp_corn


def download_and_save_asset_prices():
    # read hsi constituents
    hsi_data_provider = HSIDataProvider()
    hist_hsi_constituents = hsi_data_provider.get_hist_hsi_constituents(save_csv=False)

    # select bear market from 2021-06-07 to 2021-09-05
    #constituents_df = hist_hsi_constituents[hist_hsi_constituents['start_date'] == '2021-06-07']
    # select bull market from 2017-09-04 to 2017-11-22
    constituents_df = hist_hsi_constituents[hist_hsi_constituents['start_date'] == '2017-09-04']
    constituents = constituents_df.apply(lambda x: HKEquityInstrument(symbol=x['symbol'], location=x['location']),
                                         axis=1).to_list()
    # initialize yahoo finance data provider
    yf_provider = YahooFinanceDataProvider()

    # download hsi index price
    #index_price = yf_provider.get_adj_close_of_stock('^HSI', '2021-06-07', '2021-09-05')
    #index_price.to_csv('hsi_index_price.csv', index=True)
    index_price = yf_provider.get_adj_close_of_stock('^HSI', '2017-09-04', '2017-11-22')
    index_price.to_csv('hsi_index_price(bull).csv', index=True)

    # download asset price
    constituents_in_yf = [con.yahoo_finance_symbol for con in constituents]
    #asset_price = yf_provider.get_multiple_stock_prices(constituents_in_yf, from_dt='2015-01-01', to_dt='2021-09-05')
    #asset_price.to_csv('hsi_con_prices_20210607.csv', index=True)
    asset_price = yf_provider.get_multiple_stock_prices(constituents_in_yf, from_dt='2012-01-01', to_dt='2017-11-22')
    asset_price.to_csv('hsi_con_prices_20170904.csv', index=True)

def algo_container():
    # To store result
    orig_asset_price = pd.read_csv('../data/HSI Index/hsi_con_prices_20170904.csv')
    #orig_asset_price = pd.read_csv('../data/HSI Index/hsi_con_prices_20210607.csv')
    orig_asset_price.set_index('Date', inplace=True)
    #asset_price = orig_asset_price[orig_asset_price.index >= '2021-06-07']
    asset_price = orig_asset_price[orig_asset_price.index >= '2017-09-04']

    # CRP
    weights = CRP().run(asset_price)
    algo_result = get_algo_result(asset_price, weights, "CRP")
    algo_result.fee = 0.2 / 100
    print(algo_result.summary())
    ########## Bear (07/06/2021 - 05/09/2021) #############################
    #{'annualized_return': -0.2686854593472205, 'annualized_volatility': 0.15518561089627508,
    #'sharpe_ratio': -1.7313812652824359, 'mdd': 0.11398309646926885, 'calmar_ratio': -2.3572395177004264,
    # 'final_wealth': 0.933257826130966}

    ########## Bull (23/10/2017 - 22/01/2018) #############################
    #{'annualized_return': 0.20515909226032236, 'annualized_volatility': 0.10388286677954997,
    # 'sharpe_ratio': 1.9749078805814138, 'mdd': 0.030035916597517365, 'calmar_ratio': 6.8304588473014975,
    # 'final_wealth': 1.043740675328894}


    # index price
    #index_price = pd.read_csv('../data/HSI Index/hsi_index_price.csv')
    index_price = pd.read_csv('../data/HSI Index/hsi_index_price(bull).csv')
    index_price.set_index('Date', inplace=True)
    index_result = get_algo_result(index_price, [1 for i in range(len(index_price))], "HSI")
    index_result.fee = 0
    print(index_result.summary())
    ########## Bear (07/06/2021 - 05/09/2021) #############################
    # {'annualized_return': -0.40591224034260037, 'annualized_volatility': 0.21547679664078853,
    #  'sharpe_ratio': -1.8837863132858712, 'mdd': 0.1515455665603621, 'calmar_ratio': -2.6784831094410237,
    #  'final_wealth': 0.8997720822192036}
    ########## Bull (23/10/2017 - 22/01/2018) #############################
    #{'annualized_return': 0.34435172656303775, 'annualized_volatility': 0.12003637926813283,
    # 'sharpe_ratio': 2.8687280361384246, 'mdd': 0.02621363506032326, 'calmar_ratio': 13.136359218040907,
    # 'final_wealth': 1.0749023464246643}

    # CORN (Time consuming)
    # Need to run between different parameter
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=10, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(orig_asset_price)
    algo_result = get_algo_result(asset_price, corn_weights[-len(asset_price):], "CORN")
    algo_result.fee = 0.2 / 100
    print(algo_result.summary())
    ########## Bear (07/06/2021 - 05/09/2021) ############################# CORN
    #{'annualized_return': -0.21119781724166015, 'annualized_volatility': 0.15692287402854893,
    # 'sharpe_ratio': -1.3458701833566789, 'mdd': 0.10745529937197351, 'calmar_ratio': -1.96544813030175,
    # 'final_wealth': 0.9465048976740286}
    ########## Bull (23/10/2017 - 22/01/2018) ############################# CORN
    #{'annualized_return': 0.35879360923368975, 'annualized_volatility': 0.1203789125949236,
    # 'sharpe_ratio': 2.980535390289114, 'mdd': 0.030786432534476216, 'calmar_ratio': 11.65427689070159,
    # 'final_wealth': 1.078218108592712}


if __name__ == "__main__":
    # Todo: Optimize different parameters
    bull_asset_prices = pd.read_csv('../data/HSI Index/hsi_con_prices_20170904.csv')
    bull_asset_prices.set_index('Date', inplace=True)
    reqs = get_algo_runner_req_corn()
    algo_runner_mp_corn(bull_asset_prices, reqs, 'data/HSI Index/Bull')



    # Todo: Min Variance Portfolio
