import os
import sys

import pandas as pd

from . import path_parser, utils


def get_serie_hashtag(size: int) -> pd.Series:

    pad_size = len(str(size))
    list_hashtag = ["#F" + str(num + 1).zfill(pad_size) for num in range(size)]
    serie_hashtag = pd.Series(list_hashtag, name="hashtag")
    return serie_hashtag


def parse_dict_to_summary(dict_, deep=0, list_string=[]):

    deep += 1
    list_file_name = []
    list_folder_name = []
    for key_, value_ in dict_.items():
        if isinstance(value_, str):
            list_file_name.append(key_)
        else:
            list_folder_name.append(key_)

    if len(list_file_name) > 0:
        string_files = " ".join(list_file_name) + "\n"
        list_string.append(string_files)
    for folder_name in list_folder_name:
        string_folder_title = "=" * deep + " " + folder_name
        list_string.append(string_folder_title)
        list_string = parse_dict_to_summary(
            dict_[folder_name], deep, list_string
        )
    return list_string


def get_serie_folder_path_relative(serie_folder_path, max_depth=0):
    """Returns the path of the relative folder of the root folder in common
    to all the file paths in the series

    Args:
        serie_folder_path (pandas.Series): Series to be parsed
    """

    def join_folders(row):

        list_folders = list(row)
        list_folders = [
            folder for folder in list_folders if folder is not None
        ]
        if list_folders:
            return os.path.join(*list_folders)
        else:
            return None

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

    df.drop(list_index_col_root, axis=1, inplace=True)
    if max_depth != 0:
        df = df.iloc[:, :max_depth]
    serie_folder_path_relative = df.apply(join_folders, axis=1)
    return serie_folder_path_relative


def gen_lines_summary(
    serie_folder_path: pd.Series, serie_hashtag: pd.Series, max_depth: int = 0
) -> list:
    """Generates the summary (without header or footer), in list format

    Args:
        serie_folder_path (pd.Series): Folder path
        serie_hashtag (pd.Series): hashtag
        max_depth (int, optional): Maximum depth of folder breakdown.
            Value 0 represents breakdown all folders. Defaults to 0.

    Returns:
        list: Summary content (without header or footer), in List of strings.
    """

    serie_folder_relative = get_serie_folder_path_relative(
        serie_folder_path, max_depth
    )

    list_path_hashtag = []
    for folder, hashtag in zip(
        serie_folder_relative.to_list(), serie_hashtag.to_list()
    ):
        if folder:
            list_path_hashtag.append(os.path.join(folder, hashtag))
        else:
            list_path_hashtag.append(hashtag)

    dict_nested = path_parser.get_tree_directory(list_path_hashtag)
    list_line_summary = parse_dict_to_summary(dict_nested, 0, list_string=[])
    return list_line_summary


def gen_lines_summary_adapted(
    serie_folder_path: pd.Series, serie_hashtag: pd.Series
) -> list:
    """Generates the summary with the highest level of folder depth possible,
    limited by a maximum of lines

    Args:
        serie_folder_path (pd.Series): folder path
        serie_hashtag (pd.Series): hashtag

    Returns:
        list: Summary content (without header or footer), in List of strings.
    """

    max_depth = 0
    max_lines = 200
    for _ in range(3):
        list_line = []
        list_line = gen_lines_summary(
            serie_folder_path, serie_hashtag, max_depth
        )
        # Decrease the depth level of folders
        #  until summary has less than 300 lines
        if len(list_line) > max_lines:
            max_depth = 3 if max_depth == 0 else max_depth - 1
        else:
            break

    if len(list_line) > max_lines:
        list_line = gen_lines_summary(
            serie_folder_path, serie_hashtag, max_depth=1
        )
    return list_line


def get_txt_content(file_path):

    list_encode = ["utf-8", "ISO-8859-1"]  # utf8, ansi
    for encode in list_encode:
        try:
            file = open(file_path, "r", encoding=encode)
            file_content = file.readlines()
            file_content = "".join(file_content)
            file.close()
            return file_content
        except:
            continue

    file = open(file_path, "r", encoding=encode)
    file_content = file.readlines()
    raise Exception("encode", f"Cannot open file: {file_path}")


def get_mid(path_report):

    df_report = pd.read_csv(path_report)
    serie_folder_path = df_report["file_path_folder_origin"]
    serie_hashtag = get_serie_hashtag(size=serie_folder_path.shape[0])

    list_line = gen_lines_summary_adapted(serie_folder_path, serie_hashtag)
    stringa = "\n".join(list_line)
    return stringa


def main(path_report, dict_summary):

    path_summary_bot = dict_summary["path_summary_bot"]
    path_summary_top = dict_summary["path_summary_top"]

    summary_top_content = get_txt_content(file_path=path_summary_top)
    mid_content = get_mid(path_report)
    summary_bot_content = get_txt_content(file_path=path_summary_bot)

    summary_content = (
        summary_top_content + "\n" + mid_content + "\n" + summary_bot_content
    )
    return summary_content
