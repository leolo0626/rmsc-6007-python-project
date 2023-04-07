from src.algo_result import AlgoResult
from src.algo_base import AlgoBase
import matplotlib.pyplot as plt
import pandas as pd

selections = ['DXCM', 'MTCH', 'ADBE', 'BIIB', 'TXN', 'PCAR', 'FAST', 'MSFT', 'GILD', 'ADI']

nasdaq100 = pd.read_csv('../../src/data/nasdaq100.csv', index_col=0)
nasdaq100.index = pd.to_datetime(nasdaq100.index, format='%Y-%m-%d %H:%M:%S')
nasdaq10 = nasdaq100[selections]
nasdaq10_price_relative = AlgoBase.transform_price_data(nasdaq10)

weight10 = pd.read_csv('result_nasdaq10_corn.csv', index_col=0)[1:]
weight10.index = nasdaq10_price_relative.index

algo_result = AlgoResult(nasdaq10_price_relative, weight10)

# Equity Curve
algo_result.equity_curve.plot(kind='line', rot=45)
plt.show()
# Each asset's performance curve
algo_result.asset_equity.plot()
plt.show()
# Decompose asset weight curve
algo_result.asset_r.plot()
plt.show()
# drawdown curve
algo_result.drawdown_curve.plot()
plt.show()

print(algo_result.summary())