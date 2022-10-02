from pathlib import Path

import pandas as pd


def explode_parts_serie_path(path_serie: pd.Series) -> pd.DataFrame:
    """Converts a series of Path into a dataframe with each column being a part
    of the Path

    Args:
        path_serie (pd.Series): Pathlib.path serie

    Returns:
        pd.DataFrame: columns with each part of Path
    """

    list_dict = path_serie.apply(lambda x: Path(x).parts).to_list()
    return pd.DataFrame(list_dict)

def check_col_unique_values(serie):

    serie_unique = serie.drop_duplicates(keep="first")
    list_unique_values = serie_unique.unique().tolist()
    qt_unique_values = len(list_unique_values)
    if qt_unique_values == 1:
        return True
    else:
        return False
