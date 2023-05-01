import streamlit as st
import plotly.express as px
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import sys

from src.utils.str_utils import extract_date_str

parent_path = str(Path(__file__).resolve().parent.parent.parent.parent)  # /online_portfolio_selection
sys.path.append(parent_path)

from src.algo_result import AlgoResult, get_algo_result
from src.algo_base import AlgoBase

from src.algo_runner import AlgoRunnerReq
from src.utils.date_utils import from_isoformat

selections = ['DXCM', 'MTCH', 'ADBE', 'BIIB', 'TXN', 'PCAR', 'FAST', 'MSFT', 'GILD', 'ADI']

nasdaq100 = pd.read_csv(parent_path + '/src/data/nasdaq100.csv', index_col=0)
nasdaq100.index = pd.to_datetime(nasdaq100.index, format='%Y-%m-%d')
nasdaq10 = nasdaq100[selections]
nasdaq10_price_relative = AlgoBase.transform_price_data(nasdaq10)


# start

def get_weight_df(data_folder, algo_req):
    df = pd.read_csv(f"{data_folder}" + '/' + algo_req.get_output_file_name(), index_col=0)
    df.index = [extract_date_str(idx) for idx in df.index]
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    return df


st.write("Analysis of Algo Results")

algo_option_list = ["13-F", "HSI", "Multi-Asset(ETFs)"]
scenario_option_list = ["BULL", "BEAR"]

algo_mapping = {
    "13-F": {
        "BULL": {
            "bt_start_date": "2021-08-16",
            "bt_end_date": "2021-11-14",
            "file_path": "data/13-F/berkshire-hathaway/Bull",
            "price_data_path": "data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2021-06-30.csv"
        },
        "BEAR": {
            "bt_start_date": "2022-08-15",
            "bt_end_date": "2022-11-13",
            "file_path": "data/13-F/berkshire-hathaway/Bear",
            "price_data_path": "data/13-F/berkshire-hathaway/berkshire-hathaway_asset_price_2022-06-30.csv"
        },
    },
    "HSI": {
        "BULL": {
            "bt_start_date": "2017-09-04",
            "bt_end_date": "2017-11-22",
            "file_path": "data/HSI Index/Bull",
            "price_data_path": "data/HSI Index/hsi_con_prices_20170904.csv"
        },
        "BEAR": {
            "bt_start_date": "2021-06-07",
            "bt_end_date": "2021-09-05",
            "file_path": "data/HSI Index/Bear",
            "price_data_path": "data/HSI Index/hsi_con_prices_20210607.csv"
        }
    },
    "Multi-Asset(ETFs)": {
        "BULL": {
            "bt_start_date": "2021-08-16",
            "bt_end_date": "2021-11-14",
            "file_path": "data/ETF/Bull",
            "price_data_path": "data/ETF/us_multi_asset_prices_bull.csv"
        },
        "BEAR": {
            "bt_start_date": "2022-08-15",
            "bt_end_date": "2022-11-13",
            "file_path": "data/ETF/Bear",
            "price_data_path": "data/ETF/us_multi_asset_prices_bear.csv"
        }
    }
}
with st.expander("Basic Configuration"):
    with st.container():
        input11, input12 = st.columns(2)
        with input11:
            algo_option = st.selectbox("Algo", algo_option_list)
        with input12:
            scenario_option = st.selectbox("Scenario", scenario_option_list)
    with st.container():
        input21, input22 = st.columns(2)
        bt_start_dt = algo_mapping.get(algo_option).get(scenario_option).get("bt_start_date")
        bt_end_dt = algo_mapping.get(algo_option).get(scenario_option).get("bt_end_date")
        file_path = algo_mapping.get(algo_option).get(scenario_option).get("file_path")
        price_data_path = algo_mapping.get(algo_option).get(scenario_option).get("price_data_path")
        with input21:
            st.date_input("Backtest Start Date", from_isoformat(bt_start_dt), disabled=True)
        with input22:
            st.date_input("Backtest End Date", from_isoformat(bt_end_dt), disabled=True)
        data_folder = f"{parent_path}/src/{file_path}"
        asset_price = pd.read_csv(f"{parent_path}/src/{price_data_path}", index_col=0)
        asset_price.index = [extract_date_str(idx) for idx in asset_price.index]
        asset_price.index = pd.to_datetime(asset_price.index, format='%Y-%m-%d')

    file_list = (file for file in os.listdir(data_folder))


# # Heat Map in the folder
algo_runner_reqs = [AlgoRunnerReq.extract_params_from_file_name(file) for file in file_list]
bt_asset_price = asset_price[(asset_price.index >= bt_start_dt) & (asset_price.index <= bt_end_dt)]
with st.expander("HeatMap"):
    tc = float(st.text_input("Transaction Fee (%): ", 0.02)) / 100
    evaluation_option = 'sharpe_ratio'
    evaluation_key = ['annualized_return', 'annualized_volatility', 'sharpe_ratio', 'mdd', 'calmar_ratio',
                      'final_wealth']
    evaluation_option = st.selectbox(
        'Select the Evaluation Key',
        evaluation_key
    )
    summary_list = []

    for algo_req in algo_runner_reqs:
        asset_weights = pd.read_csv(f"{data_folder}" + '/' + algo_req.get_output_file_name(), index_col=0)

        bt_asset_weights = asset_weights[(asset_weights.index >= bt_start_dt) & (asset_weights.index <= bt_end_dt)]
        algo_result = get_algo_result(bt_asset_price, bt_asset_weights.to_numpy(), "CORN")
        algo_result.fee = tc
        summary_dict = algo_result.summary()
        summary_dict.update(algo_req.params)
        summary_list.append(summary_dict)
    df = pd.DataFrame(summary_list)
    result = df.pivot(index='window_size', columns='corr_threshold', values=evaluation_option)
    fig = plt.figure(figsize=(10, 4))
    sns.heatmap(result, annot=True, fmt="g", cmap="viridis")
    st.pyplot(fig)

with st.container():
    input31, input32, input33 = st.columns(3)
    with input31:
        window_size = st.selectbox("Window Size: ",
                                   sorted(set(int(req.params.get("window_size")) for req in algo_runner_reqs)))
    with input32:
        corr_threshold = st.selectbox("Corr threshold: ",
                                      sorted(set(float(req.params.get("corr_threshold")) for req in algo_runner_reqs)))
    with input33:
        opt_weight_param = st.selectbox("Optimize Weight Params: ",
                                        set(req.params.get("opt_weights_param") for req in algo_runner_reqs))

target_algo_req = [
    req
    for req in algo_runner_reqs
    if int(window_size) == int(
        req.params.get("window_size")) and float(corr_threshold) == float(req.params.get("corr_threshold"))
       and opt_weight_param == req.params.get("opt_weights_param")
][0]

# print(target_algo_req.get_output_file_name())
with st.expander("Single Algo Result"):
    single_algo_weight = get_weight_df(data_folder, target_algo_req)
    bt_single_algo_weight = single_algo_weight[(single_algo_weight.index >= bt_start_dt) &
                                               (single_algo_weight.index <= bt_end_dt)]
    algo_result = get_algo_result(bt_asset_price, bt_single_algo_weight.to_numpy(), "CORN")

    #
    algo_result.fee = 0.02 / 100
    tc = float(st.text_input("Transaction Fee (%): ", 0.02, key='tc-for-single-file')) / 100
    algo_result.fee = tc
    algo_result_summary = algo_result.summary()
    # matrix
    col1, col2, col3 = st.columns(3)
    col1.metric("Annual Return (%)", f"{algo_result_summary['annualized_return'] * 100:.4f}")
    col2.metric("Annual Vol (%)", f"{algo_result_summary['annualized_volatility'] * 100:.4f}")
    col3.metric("sharpe Ratio", f"{algo_result_summary['sharpe_ratio']:.4f}")
    col4, col6, col5 = st.columns(3)
    col4.metric("Max Drawdown (%)", f"{algo_result_summary['mdd'] * 100:.4f}")
    col5.metric("Calmar Ratio", f"{algo_result_summary['calmar_ratio']:.4f}")
    col6.metric("Total Wealth", f"{algo_result_summary['final_wealth']:.4f}")
    # charts
    with st.container():
        st.write("###Equity Curve")
        equity_curve_df = pd.DataFrame(
            {algo_result.algo_name: algo_result.equity_curve},
        )

        fig = px.line(equity_curve_df)
        fig.update_layout(legend=dict(orientation="h"))
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    # Each asset's performance curve
    with st.container():
        st.write("### Asset's performance curve")
        fig = px.line(algo_result.asset_equity)
        fig.update_layout(legend=dict(orientation="h"))
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    with st.container():
        st.write("### Decompose asset weight curve")
        fig = px.line(algo_result.equity_decomposed)
        fig.update_layout(legend=dict(orientation="h"))
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with st.container():
        st.write("### Position chart")
        fig = px.area(algo_result.B)
        fig.update_layout(legend=dict(orientation="h"))
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with st.container():
        st.write("### Drawdown Curve")
        st.area_chart(algo_result.drawdown_curve)
