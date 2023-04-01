from src.data_provider.yahoo_finance_data_provider import YahooFinanceDataProvider
from src.data_provider.data_helper import count_na_in_dataframe


def test_get_historical_stock_price():
    yf_data_provider = YahooFinanceDataProvider()
    # data1 = yf_data_provider.get_multiple_stock_prices(['0700.HK', 'AAPL'] , '2010-01-01', '2021-01-01')
    # print(data1)
    nasdaq100 = [
        "AAPL",
        "MSFT",
        "AMZN",
        "GOOG",
        "META",
        "TSLA",
        "NVDA",
        "PYPL",
        "ADBE",
        "CMCSA",
        "CSCO",
        "NFLX",
        "PEP",
        "INTC",
        "COST",
        "AVGO",
        "TMUS",
        "TXN",
        "QCOM",
        "MRNA",
        "HON",
        "CHTR",
        "INTU",
        "SBUX",
        "AMGN",
        "AMD",
        "ISRG",
        "AMAT",
        "GILD",
        "ADP",
        "MDLZ",
        "MELI",
        "BKNG",
        "LRCX",
        "ZM",
        "MU",
        "CSX",
        "ILMN",
        "FISV",
        "ADSK",
        "REGN",
        "ATVI",
        "ASML",
        "ADI",
        "IDXX",
        "NXPI",
        "DOCU",
        "ALGN",
        "BIIB",
        "JD",
        "MNST",
        "VRTX",
        "EBAY",
        "KLAC",
        "DXCM",
        "KDP",
        "LULU",
        "MRVL",
        "EXC",
        "KHC",
        "TEAM",
        "AEP",
        "SNPS",
        "WDAY",
        "ROST",
        "WBA",
        "MAR",
        "PAYX",
        "ORLY",
        "CDNS",
        "CTAS",
        "CTSH",
        "EA",
        "MCHP",
        "XEL",
        "BIDU",
        "MTCH",
        "XLNX",
        "CPRT",
        "FAST",
        "VRSK",
        "ANSS",
        "PTON",
        "PDD",
        "SWKS",
        "SGEN",
        "OKTA",
        "PCAR",
        "CDW",
        "MXIM",
        "NTES",
        "SIRI",
        "CERN",
        "VRSN",
        "SPLK",
        "DLTR",
        "INCY",
        "CHKP",
        "TCOM",
        "FOX",
    ]
    data = yf_data_provider.get_multiple_stock_prices(nasdaq100, '2010-01-01', '2022-12-31')
    data.to_csv('nasdaq100.csv')
    print(count_na_in_dataframe(data))
