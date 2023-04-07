import os

from src.algo_result import AlgoResult
from src.algo_base import AlgoBase
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

selections = ['DXCM', 'MTCH', 'ADBE', 'BIIB', 'TXN', 'PCAR', 'FAST', 'MSFT', 'GILD', 'ADI']


nasdaq100 = pd.read_csv('../../src/data/nasdaq100.csv', index_col=0)
nasdaq100.index = pd.to_datetime(nasdaq100.index, format='%Y-%m-%d %H:%M:%S')
nasdaq10 = nasdaq100[selections]
nasdaq10_price_relative = AlgoBase.transform_price_data(nasdaq10)

# weight10 = pd.read_csv('result_nasdaq10_crp.csv', index_col=0)[1:]
# # weight10 = pd.read_csv('result_nasdaq10_corn_60_0.3.csv', index_col=0)[1:]
# weight10.index = nasdaq10_price_relative.index
# weight10.columns = selections
# #
# algo_result = AlgoResult(nasdaq10_price_relative, weight10)
# algo_result.fee = 0.02/100
#
# # Equity Curve
# algo_result.equity_curve.plot(kind='line', rot=45)
# plt.show()
# # Each asset's performance curve
# algo_result.asset_equity.plot()
# plt.show()
# # Decompose asset weight curve
# algo_result.asset_r.plot()
# plt.show()
# # drawdown curve
# algo_result.drawdown_curve.plot()
# plt.show()
#
# print(algo_result.summary())

summary_list = []
main_path = './data/nasdaq10_corn_10'
for file_path in os.listdir(main_path):
    _, _, _, *args = file_path.replace(".csv", "").split("_")
    weight10 = pd.read_csv(main_path+'/'+file_path, index_col=0)[1:]
    weight10.index = nasdaq10_price_relative.index
    weight10.columns = selections
    algo_result = AlgoResult(nasdaq10_price_relative, weight10)
    algo_result.fee = 0.02 / 100
    summary_dict = algo_result.summary()
    for i, arg in enumerate(args):
        summary_dict.update({
            f'args_{i}': arg
        })
    summary_list.append(summary_dict)

df = pd.DataFrame(summary_list)
result = df.pivot(index='args_0', columns='args_1', values='sharpe_ratio')
sns.heatmap(result, annot=True, fmt="g", cmap="viridis")
plt.show()

benchmark_weight10 = pd.read_csv('result_nasdaq10_crp.csv', index_col=0)[1:]
benchmark_weight10.index = nasdaq10_price_relative.index
benchmark_weight10.columns = selections
benchmark_algo_result = AlgoResult(nasdaq10_price_relative, benchmark_weight10)
benchmark_algo_result.fee = 0.02 / 100
print(benchmark_algo_result.summary())
