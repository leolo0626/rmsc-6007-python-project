import streamlit as st
import plotly.express as px
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import sys

parent_path = str(Path(__file__).resolve().parent.parent.parent.parent)  # /online_portfolio_selection
sys.path.append(parent_path)

from src.algo_result import AlgoResult
from src.algo_base import AlgoBase

selections = ['DXCM', 'MTCH', 'ADBE', 'BIIB', 'TXN', 'PCAR', 'FAST', 'MSFT', 'GILD', 'ADI']

nasdaq100 = pd.read_csv(parent_path + '/src/data/nasdaq100.csv', index_col=0)
nasdaq100.index = pd.to_datetime(nasdaq100.index, format='%Y-%m-%d %H:%M:%S')
nasdaq10 = nasdaq100[selections]
nasdaq10_price_relative = AlgoBase.transform_price_data(nasdaq10)

# start

st.write("Analysis of Algo Results")

folder_option_list = (file for file in os.listdir(parent_path + '/tests/src/data'))
folder_option = st.selectbox(
    'Select the folder',
    folder_option_list
)
st.write('You selected', folder_option)

# Heat Map in the folder
heatmap_enabled = st.checkbox("Enable heatmap")
if heatmap_enabled:
    tc = float(st.text_input("Transaction Fee (%): ", 0.02)) / 100
    st.write("The current TC: ", tc)
    evaluation_option = 'sharpe_ratio'
    evaluation_key = ['annualized_return', 'annualized_volatility', 'sharpe_ratio', 'mdd', 'calmar_ratio',
                      'final_wealth']
    evaluation_option = st.selectbox(
        'Select the Evaluation Key',
        evaluation_key
    )
    st.write('You selected', evaluation_option)
    summary_list = []
    main_path = parent_path + f'/tests/src/data/{folder_option}'
    for file_path in os.listdir(main_path):
        _, _, _, *args = file_path.replace(".csv", "").split("_")
        weight10 = pd.read_csv(main_path + '/' + file_path, index_col=0)[1:]
        weight10.index = nasdaq10_price_relative.index
        weight10.columns = selections
        algo_result = AlgoResult(nasdaq10_price_relative, weight10)
        algo_result.fee = tc
        summary_dict = algo_result.summary()
        for i, arg in enumerate(args):
            summary_dict.update({
                f'args_{i}': arg
            })
        summary_list.append(summary_dict)
    df = pd.DataFrame(summary_list)
    result = df.pivot(index='args_0', columns='args_1', values=evaluation_option)
    fig = plt.figure(figsize=(10, 4))
    sns.heatmap(result, annot=True, fmt="g", cmap="viridis")
    st.pyplot(fig)

# Each File
option_list = (file for file in os.listdir(parent_path + f'/tests/src/data/{folder_option}'))
option = st.selectbox(
    'Select the result',
    option_list
)
st.write('You selected', option)

benchmark_weight10 = pd.read_csv(parent_path + f'/tests/src/data/{folder_option}/' + option, index_col=0)[1:]
benchmark_weight10.index = nasdaq10_price_relative.index
benchmark_weight10.columns = selections
benchmark_algo_result = AlgoResult(nasdaq10_price_relative, benchmark_weight10)
benchmark_algo_result.fee = 0.02 / 100
tc = float(st.text_input("Transaction Fee (%): ", 0.02, key='tc-for-single-file')) / 100
st.write("The current TC: ", tc)
benchmark_algo_result.fee = tc
benchmark_result_summary = benchmark_algo_result.summary()
st.write(benchmark_algo_result.summary())
# matrix
col1, col2, col3 = st.columns(3)
col1.metric("Annual Return (%)", f"{benchmark_result_summary['annualized_return'] * 100:.4f}")
col2.metric("Annual Vol (%)", f"{benchmark_result_summary['annualized_volatility'] * 100:.4f}")
col3.metric("sharpe Ratio", f"{benchmark_result_summary['sharpe_ratio']:.4f}")
col4, col6, col5 = st.columns(3)
col4.metric("Max Drawdown (%)", f"{benchmark_result_summary['mdd'] * 100:.4f}")
col5.metric("Calmar Ratio", f"{benchmark_result_summary['calmar_ratio']:.4f}")
col6.metric("Total Wealth", f"{benchmark_result_summary['final_wealth']:.4f}")
# charts
st.line_chart(benchmark_algo_result.equity_curve)
# Each asset's performance curve
fig = px.line(benchmark_algo_result.asset_equity)
fig.update_layout(legend=dict(orientation="h"))
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
# # Decompose asset weight curve
fig = px.line(benchmark_algo_result.equity_decomposed)
fig.update_layout(legend=dict(orientation="h"))
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
# Position chart
fig = px.area(benchmark_algo_result.B)
fig.update_layout(legend=dict(orientation="h"))
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
# # drawdown curve
st.area_chart(benchmark_algo_result.drawdown_curve)

