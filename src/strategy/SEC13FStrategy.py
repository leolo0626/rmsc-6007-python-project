from src.algo.CORN import CORN
from src.algo.CRP import CRP
from src.algo_result import get_algo_result
from src.data_provider.fintel_data_provider import FintelDataProvider
from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
import pandas as pd

# print(assets)
# 2022-08-15 #2022-11-14
from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam


def download_and_save_asset_prices():
    current_holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2022-06-30')
    assets = current_holdings.symbol.tolist()
    yf_provider = YahooFinanceDataProvider()
    asset_price = yf_provider.get_multiple_stock_prices(assets, from_dt='2017-01-01',
                                                        to_dt='2022-11-13')
    asset_price.to_csv('../data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2022-06-30.csv',
                       index=True)


if __name__ == "__main__":
    backtest_start = '2022-08-15'
    backtest_end = '2022-11-13'
    current_holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2022-06-30')
    assets = current_holdings.symbol.tolist()
    orig_asset_price = pd.read_csv('../data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2022-06-30.csv')
    orig_asset_price.set_index('Date', inplace=True)
    asset_price = orig_asset_price[(orig_asset_price.index >= backtest_start)
                                   & (orig_asset_price.index <= backtest_end)]

    # Current holding for price only
    ch_for_price_only = current_holdings[current_holdings.symbol.isin(asset_price.columns)]
    ch_for_price_only['portfolio_weight_price_only'] = ch_for_price_only.current_value_1000 / \
                                                       ch_for_price_only.current_value_1000.sum()
    # CRP
    weights = CRP().run(asset_price)
    algo_result = get_algo_result(asset_price, weights)
    algo_result.fee = 0.02 / 100
    print(algo_result.summary())
    # {'annualized_return': -0.1452614281134963, 'annualized_volatility': 0.26936484890803614,
    #  'sharpe_ratio': -0.5392738833680931, 'mdd': 0.1634983188400052, 'calmar_ratio': -0.8884582370271646,
    #  'final_wealth': 0.9557888539134486}

    # benchmark
    benchmark_weight = [ch_for_price_only[ch_for_price_only['symbol'] == a].iloc[0].portfolio_weight_price_only
                        for a in asset_price.columns]
    benchmark_weight_t = [benchmark_weight] * len(asset_price)
    algo_result = get_algo_result(asset_price, benchmark_weight_t)
    algo_result.fee = 0.02 / 100
    print(algo_result.summary())
    # {'annualized_return': -0.16150795788804517, 'annualized_volatility': 0.29653221064692137,
    #  'sharpe_ratio': -0.5446556970512437, 'mdd': 0.1701732083804789, 'calmar_ratio': -0.9490798194680583,
    #  'final_wealth': 0.9501376375388245}

    # CORN
    opt_weight_param = TCAdjustedReturnOptWeightParam(
        fee=0.2 / 100,
        lda=0.5
    )
    corn_weights = CORN(window_size=10, corr_threshold=0.3, opt_weights_param=opt_weight_param).run(orig_asset_price)

    algo_result = get_algo_result(asset_price, corn_weights[-len(asset_price):])
    algo_result.fee = 0.02 / 100
    print(algo_result.summary())
    # {'annualized_return': -0.1452614281134963, 'annualized_volatility': 0.26936484890803614,
    #  'sharpe_ratio': -0.5392738833680931, 'mdd': 0.1634983188400052, 'calmar_ratio': -0.8884582370271646,
    #  'final_wealth': 0.9557888539134486}
    # Todo: Optimize different parameters

    # Todo: Min Variance Portfolio
