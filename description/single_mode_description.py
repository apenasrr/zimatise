import os
import sys
from pathlib import Path

import pandas as pd

from . import utils

script_path = Path(__file__).absolute()
script_folder_path = script_path.parent
folder_timestamp_link_maker = (
    script_folder_path.parent / "timestamp_link_maker"
)

sys.path.append(str(folder_timestamp_link_maker))
from timestamp_link_maker import timestamp_link_maker


def get_df_desc_draft(serie_folder_relative, serie_file_name):
    """Create a dataframe with columns ["folder_relative", "file_name"]
    from separate series.

    Args:
        serie_folder_relative (pandas.Series): folder_relative serie
        serie_file_name (pandas.Series): file_name serie

    Returns:
        pandas.DataFrame:
            Dataframe with columns ["folder_relative", "file_name"]
    """

    df_desc_draft = pd.concat([serie_folder_relative, serie_file_name], axis=1)
    df_desc_draft.columns = ["folder_relative", "file_name"]
    return df_desc_draft


def create_text_desc(row):
    """From a dictionary that corresponds all data from a dataframe line,
    create the file description.

    Args:
        row (dict): From a dataframe apply in column (axis=1)
    """

    def get_list_folder_lines(list_folder):
        list_folder_lines = []
        for index, folder in enumerate(list_folder):
            if folder:
                list_folder_lines.append("=" * (index) + folder)
        return list_folder_lines

    folder_relative = row["folder_relative"]
    file_name = row["file_name"]
    if folder_relative:
        tuple_folder = Path(folder_relative).parts
        list_folder_lines = get_list_folder_lines(tuple_folder)
        str_folder_lines = "\n\n" + "\n".join(list_folder_lines)

    else:
        str_folder_lines = ""
    desc = file_name + str_folder_lines
    return desc


def get_serie_description(df):
    serie_description_draft = df.apply(create_text_desc, axis=1)
    serie_description = include_hashtag(serie_description_draft)
    return serie_description


def include_hashtag(serie_input):
    """Includes "#F00" at the beginning of each line of the series.
    The number will be a sequencial number with padding standardized
    to settle the total number of lines.
    If there are between 1 and 9 lines, there will be a padding of 1 digit.
    If there are between 10 and 99 lines, there will be a 2 digit padding.
    And so on.

    Args:
        serie_input (pandas.series): Serie to be transformed

    Returns:
        _type_: Serie transformed
    """

    rows_count = serie_input.shape[0]
    pad_size = len(str(rows_count))

    serie_output = serie_input.copy()
    for index, desc_raw in enumerate(serie_output):
        description = "#F" + str(index + 1).zfill(pad_size) + " " + desc_raw
        serie_output[index] = description
    return serie_output


def get_folder_path_root(serie_folder_path):
    """Returns the path of the root folder in common to all the file paths in
    the series

    Args:
        serie_folder_path (pandas.series): Series to be parsed
    """

    # create dataframe with columns as sequencial integer and folders as values
    df = utils.explode_parts_serie_path(serie_folder_path)
    len_cols = len(df.columns)

    list_index_col_root = []
    for n_col in range(len_cols - 1):
        serie = df.iloc[:, n_col]
        # check for column with more than 1 unique value (folder root)
        col_has_one_unique_value = utils.check_col_unique_values(serie)
        if col_has_one_unique_value:
            # name col is a sequencial integer
            name_col = df.columns[n_col]
            list_index_col_root.append(name_col)
        else:
            break
    if len(list_index_col_root) == 0:
        raise ValueError("No root folder found")

    list_parts = df.iloc[0, list_index_col_root].to_list()
    folder_path_root = Path(*list_parts)
    return folder_path_root


def get_serie_subfolders(
    serie_folder_path: pd.Series, folder_path_root: str
) -> pd.Series(Path):
    """Excludes the path of the root folder, from a path of absolute paste"""

    def exclude_root_folder_parts(folder_path, folder_path_root):
        tuple_parts = Path(folder_path).parts[len(folder_path_root.parts) :]
        return Path(*tuple_parts)

    serie_subfolders = serie_folder_path.apply(
        lambda folder_path: exclude_root_folder_parts(
            folder_path, folder_path_root
        )
    )
    return serie_subfolders


def create_df_descriptions(file_path_report_origin):
    """Create a custom description report from a file report.
    Columns required:
        ["file_path_folder",
        "file_name",
        "file_path_folder_origin",
        "file_name_origin",
        "file_output"]
    Args:
        file_path_report_origin (str): Report path in csv format

    Returns:
        pandas.DataFrame:
            dataframe with columns ["file_output", "description", "warning]
    """

    list_columns_keep = [
        "file_path_folder",
        "file_name",
        "file_path_folder_origin",
        "file_name_origin",
    ]
    df_video_details = timestamp_link_maker.get_df_source(
        file_path_report_origin, list_columns_keep=list_columns_keep
    )
    serie_file_name = df_video_details["file_name_origin"].apply(
        lambda x: os.path.splitext(x)[0]
    )

    serie_folder_path = df_video_details["file_path_folder_origin"]
    folder_path_root = get_folder_path_root(
        serie_folder_path=serie_folder_path
    )

    serie_folder_relative = get_serie_subfolders(
        serie_folder_path, folder_path_root
    )

    df_desc_draft = get_df_desc_draft(serie_folder_relative, serie_file_name)
    serie_description = get_serie_description(df_desc_draft)

    df_description = pd.DataFrame()
    df_description["file_output"] = df_video_details[
        ["file_path_folder", "file_name"]
    ].apply(lambda row: Path(*row), axis=1)

    df_description["description"] = serie_description
    df_description["warning"] = ""

    return df_description
