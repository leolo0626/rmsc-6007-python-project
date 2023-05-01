from datetime import datetime


def from_isoformat(date_str):
    return datetime.fromisoformat(date_str)