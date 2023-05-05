import bs4
import pandas as pd
import requests
import numpy as np
import os


class FintelDataProvider:
    # https://fintel.io/i13fs/berkshire-hathaway
    URL_PREFIX = "https://fintel.io/"
    HEADER = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    def __init__(self, abs_parent_path=None):
        self.abs_parent_path = abs_parent_path
        self.save_path_prefix = self._get_path('data/13-F/')

    def _get_path(self, file_path):
        if self.abs_parent_path:
            return f'{self.abs_parent_path}/{file_path}'
        else:
            return f'../{file_path}'

    def get_default_fund_folder(self, fund_name):
        return f'{self.save_path_prefix}{fund_name}'

    def get_filing_summary(self, fund_name: str, save_to_csv: bool = False):
        url = f"{self.URL_PREFIX}/i13fs/{fund_name}"
        r = requests.get(url, headers=self.HEADER)
        print(r.status_code, r.text)
        sp = bs4.BeautifulSoup(r.text, 'lxml')
        tb = sp.find_all('table')[1]
        df = pd.read_html(str(tb), encoding='utf-8')[0]
        df['href'] = [np.where(tag.has_attr('href'), tag.get('href'), "no link") for tag in
                      tb.find_all('a')]

        if save_to_csv:
            folder_path = self.get_default_fund_folder(fund_name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            df.to_csv(f'{folder_path}/{fund_name}.csv', index=False)
        return df

    def get_raw_holding_data(self, fund_name: str, reporting_period: str, force_update: bool = False,
                             save_to_csv: bool = False):
        # check fund name already in the folder or not
        folder_path = self.get_default_fund_folder(fund_name)
        filepath = f'{folder_path}/{fund_name}.csv'
        holding_filepath = f'{folder_path}/{fund_name}_{reporting_period}.csv'
        if os.path.exists(holding_filepath) and not force_update:
            print(f"{fund_name} holding report at {reporting_period} exists in the folder")
            return pd.read_csv(holding_filepath)

        if not os.path.exists(filepath):
            summary = self.get_filing_summary(fund_name, save_to_csv=True)
        else:
            summary = pd.read_csv(filepath)

        temp_df = summary[(summary['Reporting Period'] == reporting_period) & (summary['Form'] == '13F-HR')]

        if len(temp_df) == 0:
            raise ValueError(f"No filings is reported at {reporting_period}")

        r = requests.get(f'{self.URL_PREFIX}{temp_df.iloc[0].href}', headers=self.HEADER)
        df = pd.read_html(r.text)[1]
        df['symbol'] = df['Security'].apply(lambda x: x.split("/")[0].strip())
        if save_to_csv:
            folder_path = self.get_default_fund_folder(fund_name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            df.to_csv(holding_filepath, index=False)
        return df

    def get_current_holdings(self, fund_name: str, reporting_period: str):
        folder_path = self.get_default_fund_folder(fund_name)
        holding_filepath = f'{folder_path}/{fund_name}_{reporting_period}.csv'
        if os.path.exists(holding_filepath):
            df = pd.read_csv(holding_filepath)
        else:
            df = self.get_raw_holding_data(fund_name, reporting_period, force_update=True, save_to_csv=True)
        df = df[['Security', 'symbol', 'Current Shares', 'Current Value (USD x1000)']]
        df.columns = ['security', 'symbol', 'current_shares', 'current_value_1000']
        df = df[df['current_shares'] != 0]
        df['portfolio_weight'] = df['current_value_1000'] / df['current_value_1000'].sum()
        return df


if __name__ == "__main__":
    holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2022-09-30')
