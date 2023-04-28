import yfinance
import pandas as pd
from typing import List
import multiprocessing as mp


class YahooFinanceDataProvider:

    def get_historical_stock_price(self, ticker: str,
                                   from_dt: str, to_dt: str) -> pd.DataFrame:
        return yfinance.download(ticker, from_dt, to_dt)

    def get_adj_close_of_stock(self, *args):
        ticker, from_dt, to_dt = args
        try:
            price = self.get_historical_stock_price(ticker, from_dt, to_dt)
            adj_close = price.rename(columns={'Adj Close': 'adj_close'}).adj_close
            adj_close.rename(ticker, inplace=True)
            return adj_close
        except Exception as e:
            print(f'Ticker[{ticker}] cannot extract stock price from yahoo finance - {str(e)}')
            return None

    def get_multiple_stock_prices(self, tickers: List[str], from_dt: str, to_dt: str):
        res = []
        args = [(ticker, from_dt, to_dt) for ticker in tickers]
        with mp.Pool() as p:
            res = p.starmap(self.get_adj_close_of_stock, args)
            res = list(filter(lambda df: df is not None, res))
        return pd.concat(res, axis=1)
