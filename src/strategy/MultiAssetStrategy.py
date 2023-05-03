# ETFS suggested by AI to cover different asset classes and styles
from src.algo.CORN import CORN
from src.algo.CRP import CRP
from src.algo_result import get_algo_result
from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
import pandas as pd
import plotly.express as px


from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam
from src.strategy.strategy_helper import get_algo_runner_req_corn, algo_runner_mp_corn


def download_and_save_asset_prices():
    ETFs = ['SPY', 'EFA', 'IEF', 'LQD', 'VNQ', 'GLD', 'USO', 'HYG', 'IWD', 'VUG', 'IWN', 'IWO', 'IWB', 'SDY', 'USMV',
            'MTUM', 'QUAL', 'LRGF']

    yf_provider = YahooFinanceDataProvider()
    ################# Bear ########################
    #asset_price = yf_provider.get_multiple_stock_prices(ETFs, from_dt='2017-01-01', to_dt='2022-11-13')
    #asset_price.to_csv('../data/ETF/us_multi_asset_prices_bear.csv',
    #                   index=True)
    ################# Bull ########################
    asset_price = yf_provider.get_multiple_stock_prices(ETFs, from_dt='2016-01-01', to_dt='2021-11-14')
    asset_price.to_csv('../data/ETF/us_multi_asset_prices_bull.csv',
                       index=True)

# Todo: Optimize different parameters

def algo_container_bull():
    backtest_start = '2021-08-16'
    backtest_end = '2021-11-14'
    orig_asset_price = pd.read_csv('../data/ETF/us_multi_asset_prices_bull.csv')
    orig_asset_price.set_index('Date', inplace=True)
    asset_price = orig_asset_price[(orig_asset_price.index >= backtest_start)
                                   & (orig_asset_price.index <= backtest_end)]
    # CRP
    weights = CRP().run(asset_price)
    crp_result = get_algo_result(asset_price, weights, "CRP")
    crp_result.fee = 0.2 / 100
    print(crp_result.summary())
    ################# Bull ########################
    # {'annualized_return': 0.17394676087795613, 'annualized_volatility': 0.09072216165688786,
    # 'sharpe_ratio': 1.9173568806244339, 'mdd': 0.037861662670064744, 'calmar_ratio': 4.594271582676342,
    # 'final_wealth': 1.043373482723385}

    # Index
    index_price = pd.DataFrame(asset_price['SPY'])
    index_result = get_algo_result(index_price, [1 for i in range(len(index_price))], "benchmark")
    index_result.fee = 0
    print(index_result.summary())
    ################# Bull ########################
    # {'annualized_return': 0.19693035435412165, 'annualized_volatility': 0.11395130149297053,
    # 'sharpe_ratio': 1.728197499931758, 'mdd': 0.0511413805389247, 'calmar_ratio': 3.85070469899095,
    # 'final_wealth': 1.0487660623786357}

    # CORN
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=10, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(orig_asset_price)

    corn_result = get_algo_result(asset_price, corn_weights[-len(asset_price):], "CORN")
    corn_result.fee = 0.2 / 100
    print(corn_result.summary())
    ################# Bull ########################
    # {'annualized_return': 0.1945308830264043, 'annualized_volatility': 0.10601163044237195,
    # 'sharpe_ratio': 1.8349956718395302, 'mdd': 0.04718347020899971, 'calmar_ratio': 4.12286086980732,
    # 'final_wealth': 1.048363796999007}

    equity_curve_df = pd.DataFrame(
        {crp_result.algo_name: crp_result.equity_curve,
         index_result.algo_name: index_result.equity_curve,
         corn_result.algo_name: corn_result.equity_curve},
    )

    fig = px.line(equity_curve_df, title='Equity Curve for Multi-Asset ETF Strategy (Bull) - 2021/08/16 to 2021/11/14')
    fig.show()


def algo_container_bear():
    backtest_start = '2022-08-15'
    backtest_end = '2022-11-13'
    orig_asset_price = pd.read_csv('../data/ETF/us_multi_asset_prices_bear.csv')
    orig_asset_price.set_index('Date', inplace=True)
    asset_price = orig_asset_price[(orig_asset_price.index >= backtest_start)
                                  & (orig_asset_price.index <= backtest_end)]

    # CRP
    weights = CRP().run(asset_price)
    crp_result = get_algo_result(asset_price, weights, "CRP")
    crp_result.fee = 0.2 / 100
    print(crp_result.summary())
    ################# Bear ########################
    # {'annualized_return': -0.1817835792070297, 'annualized_volatility': 0.22054123494425962,
    # 'sharpe_ratio': -0.8242611829618818, 'mdd': 0.13969165879989487, 'calmar_ratio': -1.3013202131662747,
    # 'final_wealth': 0.9498798816852565}

    # Index
    index_price = pd.DataFrame(asset_price['SPY'])
    index_result = get_algo_result(index_price, [1 for i in range(len(index_price))], "benchmark")
    index_result.fee = 0
    print(index_result.summary())
    ################# Bear ########################
    # {'annualized_return': -0.2406170015909761, 'annualized_volatility': 0.2725629556374567,
    #  'sharpe_ratio': -0.8827942191492348, 'mdd': 0.1668032180043243, 'calmar_ratio': -1.4425201412165694,
    #  'final_wealth': 0.9330481574567427}

    # CORN
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=10, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(
        orig_asset_price)

    corn_result = get_algo_result(asset_price, corn_weights[-len(asset_price):], "CORN")
    corn_result.fee = 0.2 / 100
    print(corn_result.summary())
    ################# Bear ########################
    # {'annualized_return': -0.14666075028987846, 'annualized_volatility': 0.19234060800363267,
    # 'sharpe_ratio': -0.762505389850429, 'mdd': 0.12047410592963059, 'calmar_ratio': -1.2173632595832966,
    # 'final_wealth': 0.9596259114353459}

    equity_curve_df = pd.DataFrame(
        {crp_result.algo_name: crp_result.equity_curve,
         index_result.algo_name: index_result.equity_curve,
         corn_result.algo_name: corn_result.equity_curve},
    )

    fig = px.line(equity_curve_df, title='Equity Curve for Multi-Asset ETF Strategy (Bear) - 2022/08/15 to 2022/11/13')
    fig.show()


    # Todo: Optimize different parameters

    # Todo: Min Variance Portfolio


if __name__ == "__main__":
    # Todo: Optimize different parameters
    #bull_asset_prices = pd.read_csv('../data/ETF/us_multi_asset_prices_bull.csv')
    #bull_asset_prices.set_index('Date', inplace=True)
    #reqs = get_algo_runner_req_corn()
    #algo_runner_mp_corn(bull_asset_prices, reqs, 'data/ETF/Bull')

    # bear_asset_prices = pd.read_csv('../data/ETF/us_multi_asset_prices_bear.csv')
    # bear_asset_prices.set_index('Date', inplace=True)
    # reqs = get_algo_runner_req_corn()
    # algo_runner_mp_corn(bear_asset_prices, reqs, 'data/ETF/Bear')
    algo_container_bear()
