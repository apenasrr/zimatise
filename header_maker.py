from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd

import utils


def logging_config():

    logfilename = "log-" + "test_haader" + ".txt"
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


def get_project_name(df):
    """
    Includes to the right of the DataFrame, columns corresponding to each
     depth level of the folder structure of the origin files
    :df: DataFrame. Requires column 'file_path_folder_origin'
    """

    path_serie = df["file_path_folder_origin"]
    df_folder = explode_parts_serie_path(path_serie)
    serie_name_project = get_serie_name_project(df_folder)
    project_name = serie_name_project.tolist()[0]
    return project_name


def get_list_video_details_path_file(path_dir, file_name):

    list_path_file = []

    for root, dirs, files in os.walk(path_dir):
        for file in files:
            if file == file_name:
                list_path_file.append(os.path.join(root, file))

    return list_path_file


def get_dataframe_concat(list_video_details_path_file):

    df = pd.DataFrame()
    for video_details_path_file in list_video_details_path_file:
        df_unique = pd.read_csv(video_details_path_file)
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


def header_maker(path_folder_output):

    # main variables declaration
    file_name_video_details = "video_details.csv"
    path_file_template_header = Path("user") / "header_template.txt"

    # get list of video_files reports
    list_video_details_path_file = get_list_video_details_path_file(
        path_dir=path_folder_output, file_name=file_name_video_details
    )

    # create dataframe unifieds
    df = get_dataframe_concat(list_video_details_path_file)

    # create variables
    duration, file_size = get_duration_filesize(df)
    project_name = get_project_name(df)
    d_keys = {
        "project_name": project_name,
        "file_size": file_size,
        "duration": duration,
    }

    # load template
    file_path = os.path.join(path_folder_output, "header_project.txt")
    template_content = utils.get_txt_content(
        file_path=path_file_template_header
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
