# ETFS suggested by AI to cover different asset classes and styles
from src.algo.CORN import CORN
from src.algo.CRP import CRP
from src.algo_result import get_algo_result
from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
import pandas as pd

from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam


def download_and_save_asset_prices():
    ETFs = ['SPY', 'EFA', 'IEF', 'LQD', 'VNQ', 'GLD', 'USO', 'HYG', 'IWD', 'VUG', 'IWN', 'IWO', 'IWB', 'SDY', 'USMV',
            'MTUM', 'QUAL', 'LRGF']

    yf_provider = YahooFinanceDataProvider()
    asset_price = yf_provider.get_multiple_stock_prices(ETFs, from_dt='2017-01-01', to_dt='2022-11-13')
    asset_price.to_csv('../data/ETF/us_multi_asset_prices_bear.csv',
                       index=True)


if __name__ == "__main__":
    backtest_start = '2022-08-15'
    backtest_end = '2022-11-13'
    orig_asset_price = pd.read_csv('../data/ETF/us_multi_asset_prices_bear.csv')
    orig_asset_price.set_index('Date', inplace=True)
    asset_price = orig_asset_price[(orig_asset_price.index >= backtest_start)
                                   & (orig_asset_price.index <= backtest_end)]

    # CRP
    weights = CRP().run(asset_price)
    algo_result = get_algo_result(asset_price, weights)
    algo_result.fee = 0.02 / 100
    print(algo_result.summary())
    # {'annualized_return': -0.17916738867926663, 'annualized_volatility': 0.2205444621004,
    #  'sharpe_ratio': -0.8123867041272749, 'mdd': 0.13942955592885475, 'calmar_ratio': -1.2850029356092079,
    #  'final_wealth': 0.9505017445287095}

    # Index
    index_price = pd.DataFrame(asset_price['SPY'])
    index_result = get_algo_result(index_price, [1 for i in range(len(index_price))])
    index_result.fee = 0
    print(index_result.summary())
    # {'annualized_return': -0.2406170015909761, 'annualized_volatility': 0.2725629556374567,
    #  'sharpe_ratio': -0.8827942191492348, 'mdd': 0.1668032180043243, 'calmar_ratio': -1.4425201412165694,
    #  'final_wealth': 0.9330481574567427}

    # CORN
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=10, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(orig_asset_price)

    algo_result = get_algo_result(asset_price, corn_weights[-len(asset_price):])
    algo_result.fee = 0.02 / 100
    print(algo_result.summary())
    # {'annualized_return': -0.14943474112414679, 'annualized_volatility': 0.18410412435845663,
    #  'sharpe_ratio': -0.8116860045633338, 'mdd': 0.11679207351165177, 'calmar_ratio': -1.2794938614497535,
    #  'final_wealth': 0.9593256695361027}