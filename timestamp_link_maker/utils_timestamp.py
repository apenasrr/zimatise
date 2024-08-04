import logging
import os
from configparser import ConfigParser
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


def adapt_description_to_limit(df):
    list_index_warning = list(df["description"][~df["warning"].isna()].index)
    for index_warning in list_index_warning:
        desc_warning = df.loc[index_warning, "description"]
        text_trimmed = trim_description_text(desc_warning)
        df.loc[index_warning, "description"] = text_trimmed
        df.loc[index_warning, "warning"] = float("nan")
    return df


def trim_description_text(desc_warning):
    """Ensures that the description will be below a thousand characters.

    Args:
        desc_warning (str): description text

    Returns:
        str: description text trimmed
    """

    len_preserv_right = 15
    hidden_symbol = "..."
    limit_len = 999
    text_trimmed = trim_block_text(
        desc_warning, limit_len, len_preserv_right, hidden_symbol
    )
    return text_trimmed


def trim_block_text(
    text_content, limit_len, len_preserv_right=15, hidden_symbol="..."
):
    if len(text_content) <= limit_len:
        return text_content

    list_line_content = text_content.split("\n")
    start_max_len = max(
        [len(line_content) for line_content in list_line_content]
    )
    max_len_allowed = start_max_len - 1

    list_newlines = list_line_content.copy()
    while True:
        for index, newlines in enumerate(list_newlines):
            if len(newlines) > max_len_allowed:
                line_trim = trim_string(
                    newlines, 1, len_preserv_right, hidden_symbol
                )
                list_newlines[index] = line_trim
            else:
                list_newlines[index] = newlines
        max_len_allowed -= 1
        text_trimmed = "\n".join(list_newlines)
        if len(text_trimmed) <= limit_len:
            break
    return text_trimmed


def trim_string(stringa, len_trim, len_preserv_right, hidden_symbol):
    len_stringa = len(stringa)
    sufix = stringa[-len_preserv_right:]

    len_prefix_after_trim = len_stringa - len_preserv_right - len_trim
    line_prefix_trim = stringa[: len_prefix_after_trim - len(hidden_symbol)]

    line_trim = line_prefix_trim + hidden_symbol + sufix
    return line_trim


def check_descriptions_warning(folder_path_project: Path):
    df_description = get_df_description(folder_path_project)
    return check_descriptions_warning_from_df(df_description)


def check_descriptions_warning_from_df(df):
    if "max size reached" in list(df["warning"].unique()):
        return True
    else:
        return False


def get_df_description(folder_path_output: Path):
    file_path_description = folder_path_output / "upload_plan.csv"
    df_desc = pd.read_csv(file_path_description)
    return df_desc


def ensure_folder_existence(folders_path):
    """
    :input: folders_path: List
    """

    for folder_path in folders_path:
        Path(folder_path).mkdir(exist_ok=True)


def get_config_data(file_path_config):
    """get default configuration data from file config.ini

    Returns:
        dict: config data
    """

    config_file = ConfigParser()
    config_file.read(file_path_config)
    default_config = dict(config_file["default"])
    return default_config


def test_unknown_items(list_items, list_known_items, name_test):
    new_items = []
    for item in list_items:
        if item not in list_known_items and item == item:
            new_items.append(item)
    if len(new_items) != 0:
        if len(new_items) > 1:
            str_items = ", ".join(new_items)
        else:
            str_items = new_items[0]
        logging.info(f"Found {name_test} not known: {str_items}")
        return False
    else:
        return True


def test_file_close(file_path):
    try:
        file_obj = open(file_path, "r+", encoding="utf-8")
        file_obj.closed
        return True
    except IOError:
        logging.error(
            "\nCould not open file! "
            + f"Please close the file!\n{file_path}\n"
        )
        return False
