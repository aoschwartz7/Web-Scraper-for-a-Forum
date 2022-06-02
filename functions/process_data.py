import pandas as pd


# class ProcessData:
#     def __init__(self) -> None:
#         pass

#     def ake


def make_df(data: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    return df


def make_big_df(data: list[pd.DataFrame]) -> pd.DataFrame:
    df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), data)
    return df
