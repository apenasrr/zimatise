from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List

import pandas as pd

import utils


def logging_config():
    logfilename = "log-" + "header_maker" + ".txt"
    logging.basicConfig(
        filename=logfilename,
        level=logging.DEBUG,
        format=" %(asctime)s-%(levelname)s-%(message)s",
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(" %(asctime)s-%(levelname)s-%(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)


def check_col_unique_values(serie):
    serie_unique = serie.drop_duplicates(keep="first")
    list_unique_values = serie_unique.unique().tolist()
    qt_unique_values = len(list_unique_values)
    if qt_unique_values == 1:
        return True
    else:
        return False


def get_serie_name_project(df_folder):
    len_cols = len(df_folder.columns)
    for n_col in range(len_cols):
        serie = df_folder.iloc[:, n_col]
        col_has_one_unique_value = check_col_unique_values(serie)
        if col_has_one_unique_value is False:
            name_col = df_folder.columns[n_col - 1]
            serie_name_project = df_folder[name_col]
            return serie_name_project
    # If you do not find a column with variable values,
    #  it is because the project has no subfolders.
    # Thus, the extraction of the folder name must be
    #  through the last column in the dataframe
    serie_name_project = df_folder.iloc[:, len_cols - 1]
    return serie_name_project


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


def get_project_name(folder_path_project: Path) -> str:
    return folder_path_project.stem.replace("_", " ")


def get_list_video_details_file_path(
    folder_path: Path, file_name
) -> List[str]:
    list_file_path = []

    for root, _, files in os.walk(str(folder_path)):
        for file in files:
            if file == file_name:
                list_file_path.append(str(Path(root) / file))

    return list_file_path


def get_dataframe_concat(list_video_details_file_path):
    df = pd.DataFrame()
    for video_details_file_path in list_video_details_file_path:
        df_unique = pd.read_csv(video_details_file_path)
        df = pd.concat([df, df_unique], ignore_index=True)
    return df


def get_duration_filesize_gross(df):
    df_filter = df.loc[:, ["file_size", "duration"]]
    df_filter["duration"] = pd.to_timedelta(df_filter["duration"])
    duration_sum = df_filter["duration"].sum()

    file_size_sum_bytes = df_filter["file_size"].sum()
    file_size_sum_mb = file_size_sum_bytes / (1024**3)
    file_size_sum_mb = round(file_size_sum_mb, 1)

    duration = duration_sum
    file_size = file_size_sum_mb
    return duration, file_size


def get_duration_filesize(df):
    duration, file_size = get_duration_filesize_gross(df)
    duration = utils.format_time_delta(duration)
    file_size = str(file_size) + " gb"
    return duration, file_size


def header_maker(folder_path_output: Path, folder_path_project: Path):
    # main variables declaration
    file_name_video_details = "video_details.csv"
    file_path_template_header = Path("user") / "header_template.txt"

    # get list of video_files reports
    list_video_details_file_path = get_list_video_details_file_path(
        folder_path=folder_path_output, file_name=file_name_video_details
    )

    # create dataframe unifieds
    df = get_dataframe_concat(list_video_details_file_path)

    # create variables
    duration, file_size = get_duration_filesize(df)
    project_name = get_project_name(folder_path_project)
    d_keys = {
        "project_name": project_name,
        "file_size": file_size,
        "duration": duration,
    }

    # load template
    file_path = folder_path_output / "header_project.txt"
    template_content = utils.get_txt_content(
        file_path=file_path_template_header
    )

    # create output_content, replacing keys to values
    output_content = utils.compile_template(d_keys, template_content)

    # save file
    utils.create_txt(file_path=file_path, stringa=output_content)

    # show message
    print(f"\n{output_content}")
    print("\n==Header Created==")


if __name__ == "__main__":
    logging_config()
    header_maker()
