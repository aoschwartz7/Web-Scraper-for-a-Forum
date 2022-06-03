import pandas as pd
from functools import reduce


def flatten_data_lists(data: list[list[dict]]) -> list[dict]:
    flat_list = [item for sublist in data for item in sublist]
    return flat_list


def make_df(data: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    return df


def make_big_df(data: list[pd.DataFrame]) -> pd.DataFrame:
    df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), data)
    return df
