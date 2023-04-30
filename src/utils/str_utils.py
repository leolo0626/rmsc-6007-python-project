import re
import pandas as pd


def str_to_array(input_str, seperator: str = r','):
    # def
    return re.split(seperator, input_str)


def extract_date_str(text):
    if isinstance(text, pd.Timestamp):
        text = text.to_pydatetime().isoformat()
    match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    return match.group()
