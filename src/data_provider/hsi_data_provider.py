from src.model.Instrument import HKEquityInstrument, IndexConstituents
import pandas as pd


def get_historical_change_of_constituents():
    # download data from https://www.hsi.com.hk/eng/indexes/all-indexes/hsi
    # process data into dataframe
    df = pd.read_excel('../data/HSI Index/historical_change_of_constituents.xlsx',
                       skiprows=[i for i in range(5)],
                       names=['effective_date', 'number_of_constituents', 'change', 'count',
                              'stock_code',
                              'listing_place', 'stock_name', 'stock_name_chi'],
                       skipfooter=5)
    # apply the model
    df['instrument'] = df.stock_code.apply(HKEquityInstrument.from_hang_seng_symbol)
    return df


def get_current_constituents_from_asstocks():
    # download data from http://www.aastocks.com/en/stocks/market/index/hk-index-con.aspx
    # process data into dataframe
    df = pd.read_excel('../data/HSI Index/AASTOCKS_Export_2023-4-16.xlsx')
    df['instrument'] = df.Symbol.apply(HKEquityInstrument.from_aastock_symbol)
    return df


def get_hist_hsi_constituents(save_csv=True):
    hsi_con_change_df = get_historical_change_of_constituents()
    curr_constituent_df = get_current_constituents_from_asstocks()
    curr_hsi_constituents = curr_constituent_df.instrument.to_list()

    hist_constituents = {}

    # find hsi constituent within the period
    end_date = '2023-04-16'
    for effective_date, group in sorted(hsi_con_change_df.groupby('effective_date'), key=lambda a: a[0], reverse=True):
        start_date = effective_date
        for idx, group_item in group.iterrows():
            if group_item['change'] == 'Add 加入':
                curr_hsi_constituents.remove(group_item['instrument'])
            elif group_item['change'] == 'Delete 刪除':
                curr_hsi_constituents.append(group_item['instrument'])

        hist_constituents[(start_date, end_date)] = curr_hsi_constituents[:]
        end_date = start_date

    # export to dataframe
    result = []
    for (start_date, end_date), constituents in hist_constituents.items():
        result.extend([{'start_date': start_date, 'end_date': end_date, **con.dict()} for con in constituents])

    hist_constituents_df = pd.DataFrame(result)
    # save as csv
    if save_csv:
        hist_constituents_df.to_csv('../data/HSI Index/hist_hsi_constituents.csv', index=False)
    return hist_constituents_df


if __name__ == "__main__":
    get_hist_hsi_constituents()