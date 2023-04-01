import pandas as pd


def count_na_in_dataframe(df: pd.DataFrame):
    return df.isna().sum()
