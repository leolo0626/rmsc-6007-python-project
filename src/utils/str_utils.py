import re


def str_to_array(input_str, seperator: str = r','):
    # def
    return re.split(seperator, input_str)

