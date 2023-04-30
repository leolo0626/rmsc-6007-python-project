from src.algo.CORN import CORN
from src.algo.CRP import CRP
from src.algo_result import get_algo_result
from src.data_provider.fintel_data_provider import FintelDataProvider
from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
import pandas as pd

# print(assets)
# 2022-08-15 #2022-11-14
from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam
#bull 2021-06-30
from src.strategy.strategy_helper import get_algo_runner_req_corn, algo_runner_mp_corn


def download_and_save_asset_prices():
    current_holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2022-06-30')
    assets = current_holdings.symbol.tolist()
    yf_provider = YahooFinanceDataProvider()
    asset_price = yf_provider.get_multiple_stock_prices(assets, from_dt='2017-01-01',
                                                        to_dt='2022-11-13')
    asset_price.to_csv('../data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2022-06-30.csv',
                       index=True)
    #current_holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2021-06-30')
    #assets = current_holdings.symbol.tolist()
    #yf_provider = YahooFinanceDataProvider()
    #asset_price = yf_provider.get_multiple_stock_prices(assets, from_dt='2016-01-01',
    #                                                    to_dt='2021-11-14')
    #asset_price.to_csv('../data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2021-06-30.csv',
    #                   index=True)


def algo_container():
    backtest_start = '2022-08-15'
    backtest_end = '2022-11-13'
    current_holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2022-06-30')
    assets = current_holdings.symbol.tolist()
    orig_asset_price = pd.read_csv('../data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2022-06-30.csv')
    #################### Bull ################################
    #backtest_start = '2021-08-16'
    #backtest_end = '2021-11-14'
    #current_holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2021-06-30')
    #assets = current_holdings.symbol.tolist()
    #orig_asset_price = pd.read_csv('../data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2021-06-30.csv')
    orig_asset_price.set_index('Date', inplace=True)
    asset_price = orig_asset_price[(orig_asset_price.index >= backtest_start)
                                   & (orig_asset_price.index <= backtest_end)]

    # Current holding for price only
    ch_for_price_only = current_holdings[current_holdings.symbol.isin(asset_price.columns)]
    ch_for_price_only['portfolio_weight_price_only'] = ch_for_price_only.current_value_1000 / \
                                                       ch_for_price_only.current_value_1000.sum()
    # CRP
    weights = CRP().run(asset_price)
    algo_result = get_algo_result(asset_price, weights, "CRP")
    algo_result.fee = 0.2 / 100
    print(algo_result.summary())
    ####################### Bear #################################
    #{'annualized_return': -0.15067973243057642, 'annualized_volatility': 0.26935071983883085,
    #'sharpe_ratio': -0.559418339482209, 'mdd': 0.16403099766230245, 'calmar_ratio': -0.9186052305844482,
    # 'final_wealth': 0.9544947884623867}
    ####################### Bull #################################
    #{'annualized_return': 0.07268065127170242, 'annualized_volatility': 0.1086472278884723,
    # 'sharpe_ratio': 0.6689600156785409, 'mdd': 0.05185758429667253, 'calmar_ratio': 1.401543327894007,
    # 'final_wealth': 1.0168550054417258}

    # benchmark
    benchmark_weight = [ch_for_price_only[ch_for_price_only['symbol'] == a].iloc[0].portfolio_weight_price_only
                        for a in asset_price.columns]
    benchmark_weight_t = [benchmark_weight] * len(asset_price)
    algo_result = get_algo_result(asset_price, benchmark_weight_t, "benchmark")
    algo_result.fee = 0.2 / 100
    print(algo_result.summary())
    ####################### Bear #################################
    #{'annualized_return': -0.16604138845046412, 'annualized_volatility': 0.29653590679385355,
    # 'sharpe_ratio': -0.5599368732296326, 'mdd': 0.17059259293376228, 'calmar_ratio': -0.9733212069467443,
    # 'final_wealth': 0.9490600435353679}
    ####################### Bull #################################
    #{'annualized_return': 0.11965429859354293, 'annualized_volatility': 0.13489322867045372,
    # 'sharpe_ratio': 0.8870296883905142, 'mdd': 0.05301199955822056, 'calmar_ratio': 2.2571172487491684,
    # 'final_wealth': 1.0280519088023816}

    # CORN
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=10, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(orig_asset_price)

    algo_result = get_algo_result(asset_price, corn_weights[-len(asset_price):], "CORN")
    algo_result.fee = 0.2 / 100
    print(algo_result.summary())
    ####################### Bear #################################
    #{'annualized_return': -0.15067973243057642, 'annualized_volatility': 0.26935071983883085,
    # 'sharpe_ratio': -0.559418339482209, 'mdd': 0.16403099766230245, 'calmar_ratio': -0.9186052305844482,
    # 'final_wealth': 0.9544947884623867}
    ####################### Bull #################################
    #{'annualized_return': 0.07268065127170242, 'annualized_volatility': 0.1086472278884723,
    # 'sharpe_ratio': 0.6689600156785409, 'mdd': 0.05185758429667253, 'calmar_ratio': 1.401543327894007,
    # 'final_wealth': 1.0168550054417258}


if __name__ == "__main__":
    # Todo: Optimize different parameters
    bear_asset_prices = pd.read_csv('../data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2022-06-30.csv')
    bear_asset_prices.set_index("Date", inplace=True)
    reqs = get_algo_runner_req_corn()
    algo_runner_mp_corn(bear_asset_prices, reqs, 'data/13-F/berkshire-hathaway/Bear')

    # Todo: Min Variance Portfolio
