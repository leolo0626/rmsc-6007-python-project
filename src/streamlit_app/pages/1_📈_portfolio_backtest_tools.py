import pandas as pd
import streamlit as st
import datetime
import base64

import sys
from pathlib import Path
from typing import List

parent_path = str(Path(__file__).resolve().parent.parent.parent.parent)  # /online_portfolio_selection
sys.path.append(parent_path)

from src.algo.CRP import CRP
from src.algo_result import get_algo_result
from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
from src.model.Instrument import Instrument
from src.data_provider.hsi_data_provider import HSIDataProvider
from src.utils.str_utils import str_to_array


def save_df(dataframe):
    return dataframe.to_csv(index=True).encode('utf-8')


@st.cache_data
def get_stock_prices(tickers: List[str], from_dt: str, to_dt: str):
    # https://docs.streamlit.io/library/api-reference/performance/st.cache
    # Todo: investigate when to clear cache.
    yf_provider = YahooFinanceDataProvider()
    stock_prices = yf_provider.get_multiple_stock_prices(tickers, from_dt=from_dt,
                                                         to_dt=to_dt)
    return stock_prices


def create_download_link(val, filename, label):
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.csv">{label}</a>'


st.set_page_config(page_title="Portfolio Backtest tool", page_icon="📈")

st.markdown("# Portfolio Backtest tool")
st.sidebar.header("Plotting Demo")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!"""
)

# SideBar status
ASSET_PRICE_STATUS_PREFIX = "1) Asset Price"
BENCHMARK_PRICE_STATUS_PREFIX = "2) Benchmark Price"
CRP_STRATEGY_STATUS_PREFIX = "3) CRP Strategy"
BENCHMARK_BUY_HOLD_PREFIX = "4) Benchmark Buy and Hold"
CORN_STRATEGY_PREFIX = "5) CORN Strategy"

asset_download_text = st.sidebar.markdown(f"{ASSET_PRICE_STATUS_PREFIX} Download")
benchmark_download_text = st.sidebar.markdown(f"{BENCHMARK_PRICE_STATUS_PREFIX} Download")
crp_strategy_text = st.sidebar.markdown(f"{CRP_STRATEGY_STATUS_PREFIX}")
benchmark_buy_and_hold_text = st.sidebar.markdown(f"{BENCHMARK_BUY_HOLD_PREFIX}")
corn = st.sidebar.markdown(f"{CORN_STRATEGY_PREFIX}")

# Main Container
with st.expander("Portfolio Model Configurations"):
    input11, input12 = st.columns(2)
    with st.container():
        with input11:
            data_source = st.selectbox("Data Source", ('13-F', 'HSI', 'Default ETF', 'Manual'))
        with input12:
            df = pd.DataFrame([{'symbol': '700', 'location': 'hk', 'weight_percent': 100}])
            if data_source == 'HSI':
                data_provider = HSIDataProvider(f'{parent_path}/src')
                df = data_provider.get_hist_hsi_constituents(save_csv=False)
                hsi_effective_date = st.selectbox("effective_date", df.start_date.unique().tolist())
                df = df[df['start_date'] == hsi_effective_date]
            elif data_source == '13-F':
                pass
            elif data_source == 'Default ETF':
                pass
            elif data_source == 'Manual':
                pass
    with st.container():
        input21, input22 = st.columns(2)
        with input21:
            backtest_start_date = st.date_input('Backtest Start Date', datetime.date(2022, 8, 15))
        with input22:
            backtest_end_date = st.date_input('Backtest End Date', datetime.date(2022, 11, 13))

    with st.container():
        input31, input32 = st.columns(2)
        with input31:
            price_start_date = st.date_input('Price Start Date', datetime.date(2022, 8, 15))
        with input32:
            price_end_date = st.date_input('Price End Date', backtest_end_date)

    with st.container():
        input41, input42 = st.columns(2)
        benchmarks = []
        with input41:
            benchmark_input = st.text_input('benchmark input', placeholder="Please input Yahoo Finance Symbol")

            if benchmark_input:
                benchmarks = str_to_array(benchmark_input)
        with input42:
            if benchmarks:
                st.multiselect('Final Benchmark', benchmarks, benchmarks)

    with st.container():
        input51, input42 = st.columns(2)
        with input51:
            transaction_fee = float(st.text_input("Transaction Fee(%)") or '0')

    with st.container():
        pass

    with st.container():
        on_run = st.button("Analyze Portfolio")

with st.expander("Asset Viewer"):
    with st.container():
        # https://docs.streamlit.io/library/api-reference/widgets/st.experimental_data_editor?ref=blog.streamlit.io
        disabled = False
        if data_source == 'HSI':
            disabled = True
        edited_df = st.experimental_data_editor(df, use_container_width=True, disabled=disabled)

# Initialize for results

algo_result_summary_df = pd.DataFrame()

# analyze the data
if on_run:

    # Convert the dataframe to Instrument basemodel
    assets = edited_df.apply(lambda x: Instrument(symbol=x['symbol'], location=x['location']),
                             axis=1).to_list()
    assets = [con.yahoo_finance_symbol for con in assets]

    asset_download_text.markdown(f'{ASSET_PRICE_STATUS_PREFIX} Start.....')
    asset_price = get_stock_prices(assets, price_start_date, price_end_date)

    download_url = create_download_link(save_df(asset_price), 'asset_price', f'{ASSET_PRICE_STATUS_PREFIX} Completed')
    asset_download_text.markdown(download_url, unsafe_allow_html=True)

    if benchmarks:
        benchmark_download_text.markdown(f'{BENCHMARK_PRICE_STATUS_PREFIX} Start.....')
        benchmarks_price = get_stock_prices(benchmarks, price_start_date, price_end_date)
        benchmarks_price_download_url = create_download_link(save_df(asset_price),
                                                             'benchmarks',
                                                             f'{BENCHMARK_PRICE_STATUS_PREFIX} Completed')
        benchmark_download_text.markdown(benchmarks_price_download_url, unsafe_allow_html=True)

    # '''
    #     ################################
    #     ||                            ||
    #     ||        Algo Result         ||
    #     ||                            ||
    #     ################################
    # '''
    algo_results = []

    orig_asset_price = asset_price
    bt_asset_price = orig_asset_price[(orig_asset_price.index >= backtest_start_date.isoformat())
                                      & (orig_asset_price.index <= backtest_end_date.isoformat())]
    # CRP
    crp_strategy_text.text(f"{CRP_STRATEGY_STATUS_PREFIX} Start....")
    CRP_algo_result = get_algo_result(bt_asset_price, CRP().run(asset_price), algo_name='CRP')
    CRP_algo_result.fee = transaction_fee / 100
    algo_results.append(CRP_algo_result)
    crp_weight_download_url = create_download_link(save_df(CRP_algo_result.weights_to_df),
                                                   CRP_algo_result.algo_name,
                                                   f'{CRP_STRATEGY_STATUS_PREFIX} Completed')
    crp_strategy_text.markdown(crp_weight_download_url, unsafe_allow_html=True)
    # Benchmarks
    benchmark_buy_and_hold_text.text(f"{BENCHMARK_BUY_HOLD_PREFIX} Start.....")
    for benchmark in benchmarks:
        # it will present when benchmark string is not empty
        bt_benchmark_price = benchmarks_price.loc[(benchmarks_price.index >= backtest_start_date.isoformat()
                                                   ) & (benchmarks_price.index <= backtest_end_date.isoformat()),
                                                  [benchmark]]

        benchmark_algo_result = get_algo_result(bt_benchmark_price, [[1] for i in range(len(bt_benchmark_price))],
                                                benchmark)
        benchmark_algo_result.fee = 0
        algo_results.append(benchmark_algo_result)
    benchmark_buy_and_hold_text.text(f"{BENCHMARK_BUY_HOLD_PREFIX} Completed.")
    # CORN

    algo_result_summary_df = pd.DataFrame([algo_result.summary() for algo_result in algo_results])

with st.expander("Algo Results"):
    if len(algo_result_summary_df) == 0:
        st.text("No Results")
    else:
        with st.container():
            # https://stackoverflow.com/questions/69875734/how-to-hide-dataframe-index-on-streamlit
            st.write("Algo Summary")
            st.dataframe(algo_result_summary_df.set_index("algo_name").transpose(), use_container_width=True)

        with st.container():
            pass
