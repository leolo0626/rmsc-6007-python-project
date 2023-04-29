from src.data_provider.fintel_data_provider import FintelDataProvider

current_holdings = FintelDataProvider().get_current_holdings('berkshire-hathaway', '2022-09-30')