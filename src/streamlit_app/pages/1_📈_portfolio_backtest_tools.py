import pandas as pd
import streamlit as st
import datetime
import base64

import sys
from pathlib import Path

from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
from src.model.Instrument import HKEquityInstrument

parent_path = str(Path(__file__).resolve().parent.parent.parent.parent)  # /online_portfolio_selection
sys.path.append(parent_path)

from src.data_provider.hsi_data_provider import HSIDataProvider


def save_df(dataframe):
    return dataframe.to_csv(index=True).encode('utf-8')


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

asset_download_text = st.sidebar.markdown("1) Asset Price Download")
benchmark_download_text = st.sidebar.markdown("2) Benchmark Price Download")
crp_strategy_text = st.sidebar.markdown("3) CRP Strategy")
benchmark_buy_and_hold_text = st.sidebar.markdown("4) Benchmark Buy and Hold")
corn = st.sidebar.markdown("5) CORN Strategy")

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
                benchmarks.append(benchmark_input)
        with input42:
            if benchmarks:
                st.multiselect('Final Benchmark', benchmarks, benchmarks)

    with st.container():
        on_run = st.button("Analyze Portfolio")

with st.expander("Asset Viewer"):
    with st.container():
        # https://docs.streamlit.io/library/api-reference/widgets/st.experimental_data_editor?ref=blog.streamlit.io
        disabled = False
        if data_source == 'HSI':
            disabled = True
        edited_df = st.experimental_data_editor(df, use_container_width=True, disabled=disabled)

with st.expander("Algo Results"):
    st.text("No Results")


if on_run:

    yf_provider = YahooFinanceDataProvider()
    if data_source == 'HSI':
        constituents = edited_df.apply(lambda x: HKEquityInstrument(symbol=x['symbol'], location=x['location']),
                                       axis=1).to_list()
        constituents_in_yf = [con.yahoo_finance_symbol for con in constituents]
        asset_download_text.markdown('1) Asset Price Download Start.....')
        asset_price = yf_provider.get_multiple_stock_prices(constituents_in_yf, from_dt=price_start_date,
                                                            to_dt=price_end_date)
        download_url = create_download_link(save_df(asset_price), 'asset_price', '1) Asset Price Download Completed')
        asset_download_text.markdown(download_url, unsafe_allow_html=True)

        if benchmarks:
            benchmark_download_text.markdown('2) Benchmarks Price Download Start.....')
            benchmarks_price = yf_provider.get_multiple_stock_prices(benchmarks, price_start_date, price_end_date)
            benchmarks_price_download_url = create_download_link(save_df(asset_price),
                                                                 'benchmarks',
                                                                 '1) Benchmarks Price Download Completed')
            benchmark_download_text.markdown(benchmarks_price_download_url, unsafe_allow_html=True)



