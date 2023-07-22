"""
    Create by: apenasrr
    Source: https://github.com/apenasrr/timestamp_link_maker

    Create automatic descriptions with a several timestamp link,
    of a video composed by the joining of several small videos

    The required spreadsheet is automatically generated
    by the app vidtool: https://github.com/apenasrr/vidtool

    How to use
    If it's your first time using the tool
    1. Execute update_libs.bat
     For the next times
    2. Make sure the spreadsheet 'video_details.csv' is in the same folder as the script
    3. Execute timestamp_link_maker.bat

    Do you wish to buy a coffee to say thanks?
    LBC (from LBRY) digital Wallet
    > bFmGgebff4kRfo5pXUTZrhAL3zW2GXwJSX

    We recommend:
    mises.org - Educate yourself about economic and political freedom
    lbry.tv - Store files and videos on blockchain ensuring free speech
    https://www.activism.net/cypherpunk/manifesto.html -  How encryption is essential to Free Speech and Privacy
"""

import datetime
import logging
import os
import subprocess
from pathlib import Path

import pandas as pd

from . import utils_timestamp


def logging_config():
    logfilename = "log-" + "timestamp_link_maker" + ".txt"
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


def include_timestamp(df):
    """
    :input: DataFrame. df. Columns required: file_output, duration
    :return: DataFrame.
    """

    def include_head_file_mark(df):
        df["head_file"] = ""
        for index, _ in df.iterrows():
            if index == 0:
                head_file = True
            else:
                head_file = (
                    df.loc[index - 1, "file_output"]
                    != df.loc[index, "file_output"]
                )
            df.loc[index, "head_file"] = head_file

        return df

    df = include_head_file_mark(df)
    df["duration"] = pd.to_timedelta(df["duration"], unit="D")
    df["time_stamp"] = datetime.timedelta(seconds=0)
    for index, _ in df.iterrows():
        if index == 0:
            pass
        else:
            if df.loc[index, "head_file"]:
                pass
            else:
                time_stamp = (
                    df.loc[index - 1, "duration"]
                    + df.loc[index - 1, "time_stamp"]
                )
                df.loc[index, "time_stamp"] = time_stamp

    return df


def timedelta_to_string(timestamp):
    timestamp_micro = datetime.timedelta(microseconds=timestamp.microseconds)
    timestamp = timestamp - timestamp_micro
    hou, min_full = divmod(timestamp.seconds, 3600)
    min_, sec = divmod(min_full, 60)
    timestamp = "%02d:%02d:%02d" % (hou, min_, sec)

    return timestamp


def get_file_name_without_extension(file_name):
    file_name_without_extension = Path(file_name).stem
    return file_name_without_extension


def sequencer_file_repeated(df, column_name):
    def to_down(df, column_name, new_column, index):
        actual = df.loc[index, column_name]
        after = df.loc[index + 1, column_name]
        if actual == after:
            df.loc[index, new_column] = actual + "_P01"
        else:
            df.loc[index, new_column] = actual
        return df

    def to_up_down(df, column_name, new_column, index, count):
        before = df.loc[index - 1, column_name]
        actual = df.loc[index, column_name]
        after = df.loc[index + 1, column_name]
        if actual == after:
            if before != actual:
                count = 1
            df.loc[index, new_column] = actual + "_P%02d" % count
        else:
            if before == actual:
                df.loc[index, new_column] = actual + "_P%02d" % count
            else:
                df.loc[index, new_column] = actual
        return df, count

    def to_up(df, column_name, new_column, index, count):
        before = df.loc[index - 1, column_name]
        actual = df.loc[index, column_name]
        if before == actual:
            df.loc[index, new_column] = actual + "_P%02d" % count
        else:
            df.loc[index, new_column] = actual
        return df

    new_column = column_name + "_seq"
    count = 1
    size_lines = df.shape[0]
    if size_lines > 1:
        for index, _ in df.iterrows():
            if index == 0:
                df = to_down(df, column_name, new_column, index)
                count += 1
            else:
                if index + 1 < size_lines:
                    df, count = to_up_down(
                        df, column_name, new_column, index, count
                    )
                    count += 1
                else:
                    df = to_up(df, column_name, new_column, index, count)

    return df


def create_df_description_without_folder(df):
    # create column time_stamp_str
    df["time_stamp"] = pd.to_timedelta(df["time_stamp"], unit="D")
    df["time_stamp_str"] = df["time_stamp"].apply(timedelta_to_string)

    # Of column file_name_origin remove extension
    df["file_name_origin"] = df["file_name_origin"].apply(
        get_file_name_without_extension
    )

    """
    #input sequencer for repeated file_name_origin
     In case of split origin files, will be different output files
      with the same source file name.
      In this case, it is necessary to differentiate the name of the source
      files in the timestamp, through a numeric sequence.
      e.g.: filename_P01, filename_P02
    """
    df = sequencer_file_repeated(df, "file_name_origin")

    # create dataframe description as df_output
    df_output = df.copy()
    df_output = df_output.loc[
        :, ["file_name_origin", "file_output", "duration", "head_file"]
    ]
    df_output = df_output.drop_duplicates(subset="file_output", keep="first")
    df_output["description"] = ""
    for index, row in df_output.iterrows():
        file_output = row["file_output"]
        mask_file_output = df["file_output"].isin([file_output])
        df_video_details = df.loc[
            mask_file_output, ["file_name_origin_seq", "time_stamp_str"]
        ]
        df_video_details = df_video_details.reset_index()
        description = ""
        for index2, row in df_video_details.iterrows():
            file_name_origin_seq = row["file_name_origin_seq"]

            folder_name = row["time_stamp_str"]
            if folder_name is None:
                logging.error(f"None Folder name: {folder_name}")
                folder_name = ""
            if index2 == 0:
                description = folder_name + " " + file_name_origin_seq
            else:
                description = (
                    f"{description} \n "
                    + f"{folder_name} {file_name_origin_seq}"
                )
        df_output.loc[index, "description"] = description

    df_output = df_output.reindex(["file_output", "description"], axis=1)

    return df_output


def create_df_description_with_folder(df):
    def show_log_about_files_in_root_folder(df_video_detail_folder):
        """Show info log, pointing the original files
            whose internal folder was not found,
            assuming they are in the root folder.

        Args:
            df_video_detail_folder (dataframe):
                required column: file_name_origin_seq
        """

        list_file_name_origin_seq = df_video_detail_folder[
            "file_name_origin_seq"
        ].tolist()
        str_list_file_name_origin_seq = ", ".join(list_file_name_origin_seq)
        logging.info(
            "It may not be a problem, "
            + "but no internal folder was identified. "
            + "Check if the original files are "
            + "in the root project folder. If so, the behavior is normal: "
            + f'"{file_output}: [{str_list_file_name_origin_seq}]"'
        )

    # create column time_stamp_str
    df["time_stamp"] = pd.to_timedelta(df["time_stamp"], unit="D")
    df["time_stamp_str"] = df["time_stamp"].apply(timedelta_to_string)

    # creat list with cols folders names
    cols_folders_start = list(df.columns).index("time_stamp") + 1
    cols_folders_finish = list(df.columns).index("time_stamp_str")
    cols_folders = list(df.columns)[cols_folders_start:cols_folders_finish]

    # Remove file extension in values from column file_name_origin
    df["file_name_origin"] = df["file_name_origin"].apply(
        get_file_name_without_extension
    )

    """
    #input sequencer for repeated file_name_origin
     In case of split origin files, will be different output files
      with the same source file name.
      In this case, it is necessary to differentiate the name of the source
      files in the timestamp, through a numeric sequence.
      e.g.: filename_P01, filename_P02
    """
    df = sequencer_file_repeated(df, "file_name_origin")

    # create dataframe description as df_output
    df_output = df.copy()
    cols_keep = ["file_name_origin", "file_output", "duration", "head_file"]
    df_output = df_output.loc[:, cols_keep]
    df_output = df_output.drop_duplicates(subset="file_output", keep="first")
    df_output["description"] = ""
    df_output["warning"] = ""
    for index, row in df_output.iterrows():
        file_output = row["file_output"]
        mask_file_output = df["file_output"].isin([file_output])

        cols_df_video_details = [
            "file_name_origin_seq",
            "time_stamp_str",
        ] + cols_folders
        df_video_details = df.loc[mask_file_output, cols_df_video_details]
        df_video_details = df_video_details.reset_index()

        description = ""
        # list of folders origin from the output file
        col_folder = cols_folders[0]
        list_folders = list(df_video_details[col_folder].unique())
        for index_folder, folder in enumerate(list_folders):
            mask_folder = df_video_details[col_folder].isin([folder])
            df_video_detail_folder = df_video_details.loc[mask_folder, :]

            if folder is None:
                show_log_about_files_in_root_folder(df_video_detail_folder)
                folder = ""

            if index_folder == 0:
                description = folder
            else:
                description = description + "\n\n" + folder
            for _, row in df_video_detail_folder.iterrows():
                file_name_origin_seq = row["file_name_origin_seq"]

                description = (
                    description
                    + "\n"
                    + row["time_stamp_str"]
                    + " "
                    + file_name_origin_seq
                )
        # check for size char limit in description
        if len(description) > 1000:
            df_output.loc[index, "warning"] = "max size reached"
        else:
            pass
        df_output.loc[index, "description"] = description

    df_output = df_output.reindex(
        ["file_output", "description", "warning"], axis=1
    )

    return df_output


def description_implant_hashtag_blocks(df, hashtag_index, add_num):
    df = df.reset_index(drop=True)
    for index, row in df.iterrows():
        description = row["description"]
        counter = index + add_num

        df.loc[
            index, "description"
        ] = f"#{hashtag_index}{counter:03d}\n\n{description}"

    return df


def description_implant_signature_bottom(df):
    def get_description_bot_content():
        folder_script_path_relative = Path(__file__).parent
        folder_script_path = folder_script_path_relative.absolute()
        file_path = folder_script_path / "description_bot.txt"
        description_bot_content = get_txt_content(file_path=file_path)
        return description_bot_content

    description_bot_content = get_description_bot_content()
    df = df.reset_index(drop=True)
    for index, row in df.iterrows():
        description = row["description"]
        df.loc[
            index, "description"
        ] = f"{description}\n\n{description_bot_content}"
    return df


def get_summary_mid_without_folder(df, keyword):
    size = df.shape[0]
    mid = ""
    for index in range(size):
        if index == 0:
            mid = f"#{keyword}%02d" % (index + 1)
        else:
            mid = f"{mid}\n#{keyword}%02d" % (index + 1)

    return mid


def create_summary(
    file_path_report_origin: Path,
    folder_path_output: Path,
    start_index_number: int,
    dict_summary: dict = {},
    hashtag_index: str = "block",
):
    """create summary.txt

    Args:
        file_path_report_origin (Path): absolute spreadsheet path.
        folder_path_output (Path): Absolute path of the folder where
                                   the file will be generated
        start_index_number (int): Initial index number at which the video
                                   summary and description should start
        dict_summary (dict, optional): file_path of txts with text to be insert
            on top and bottom of output file summary.txt. Defaults to {}.
            keys: [path_summary_top, path_summary_bot]
    """

    path_summary_top = dict_summary["path_summary_top"]
    summary_top_content = get_txt_content(file_path=path_summary_top)

    df = pd.read_csv(file_path_report_origin)
    int_skip_cols = len(df.columns)
    int_col_position_folder_structure = int_skip_cols

    df = include_cols_folders_structure(df)

    summary_mid_content = get_summary_mid_with_folder(
        df,
        folder_col=int_col_position_folder_structure,
        start_index_number=start_index_number,
        hashtag_index=hashtag_index,
    )

    path_summary_bot = dict_summary["path_summary_bot"]
    summary_bot_content = get_txt_content(file_path=path_summary_bot)

    summary_content = (
        f"{summary_top_content}\n"
        + f"{summary_mid_content}\n"
        + f"{summary_bot_content}"
    )

    file_path = folder_path_output / "summary.txt"
    create_txt(file_path=file_path, stringa=summary_content)


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


def create_txt(file_path: Path, stringa):
    f = open(file_path, "w", encoding="utf8")
    f.write(stringa)
    f.close()


def get_summary_mid_with_folder(
    df, folder_col, start_index_number: int = 1, hashtag_index: str = "Block"
):
    """Create text file, marking the output files with hashtag ref string
        and informing above, the your folder structure that originate each one

    Examples:

        Vídeos

        folder_name_1
        #Block001

        folder_name_2
        #Block002

        folder_name_3
        #Block003

    Args:
        df (dataframe): required columns:
                            'file_output', listing absolute path file
        hashtag_index (str): prefix to mark each topic in summary,
                              like: 'Block'
        folder_col (int): column number position where
                          'folder depth level columns' start
        start_index_number (int): Initial index number at which the video
                                   summary and description should start

    """

    def get_dict_file_folders(list_file_output, df_folder, folder_col):
        """
        :list_file_output: List.
        :df_folder: DataFrame. Must contain column 'file_output'
        :return: list of dict, containing all origin folders
                  of each file_output
        """

        def get_list_folders_from_file_output(
            file_output, df_folder, folder_col
        ):
            """informs in a list, all the folders to which
                each aggregated video file was originated

            Args:
                file_output (str): absolute path file in search
                df_folder (dataframe): Need columns: file_output
                folder_col (int): column number position where
                                  'folder depth level columns' start

            Returns:
                list: All absolute paths of folders where the video files
                       that originated the file
                       informed in parameter (file_output)
            """

            mask_file_output = df_folder["file_output"].isin([file_output])

            # TODO: Replace line below to an 'iterate from col all cols of
            #       folders [col_number]'
            col_name = df_folder.columns[folder_col]

            serie_file_folder = df_folder.loc[mask_file_output, col_name]
            list_file_folder = serie_file_folder.unique().tolist()

            return list_file_folder

        dict_file_folder = {}
        # iterate for each file_output, looking for their corresponding source
        #  folders in df_folder
        for file_output in list_file_output:
            list_folders_file_output = get_list_folders_from_file_output(
                file_output, df_folder, folder_col
            )
            dict_file_folder[file_output] = list_folders_file_output

        return dict_file_folder

    def get_summary_mid_content_with_folders(
        list_file_output, dict_file_folders, start_index_number
    ):
        mid = ""
        for index, file_output in enumerate(list_file_output):
            list_folders = dict_file_folders[file_output]

            # for files in root folder.
            # The folder will be shown as blank string

            list_folders = [
                "" if value is None else value for value in list_folders
            ]

            str_folders = "\n".join(list_folders)

            index_hashtag = index + start_index_number
            str_mark = f"#{hashtag_index}%03d" % (index_hashtag)

            if index == 0:
                mid = str_folders + "\n" + str_mark
            else:
                mid = mid + "\n\n" + str_folders + "\n" + str_mark
        return mid

    # get file_output unique values
    list_file_output = df["file_output"].unique()
    dict_file_folders = get_dict_file_folders(list_file_output, df, folder_col)
    summary_mid_content_raw = get_summary_mid_content_with_folders(
        list_file_output=list_file_output,
        dict_file_folders=dict_file_folders,
        start_index_number=start_index_number,
    )

    summary_mid_content = summary_compact(summary_mid_content_raw)

    return summary_mid_content


def summary_compact(stringa):
    new_stringa = stringa.strip("\n").split("\n")
    d = {}
    for index, line in enumerate(new_stringa):
        if line == "":
            continue
        if line[0] != "#":
            value_next_line = new_stringa[index + 1]
            try:
                d[line] = d[line] + "; " + value_next_line
            except:
                d[line] = value_next_line

    stringa_output = ""
    for key, value in d.items():
        stringa_output = stringa_output + "\n" + key + "\n" + value + "\n"
    return stringa_output


def remove_root_folders(df, skip_cols):
    """Remove root folders columns.
        Since each folder level has been divided into a column,
        a root folder column is one whose value does not change
        for all files in the project.

    Args:
        df (dataframe): table in analysis
        skip_cols (int): number of initial columns that are not about
                          folders structure
    """

    def check_col_unique_values(serie):
        serie_unique = serie.drop_duplicates(keep="first")
        list_unique_values = serie_unique.unique().tolist()
        qt_unique_values = len(list_unique_values)
        if qt_unique_values == 1:
            return True
        else:
            return False

    len_cols = len(df.columns)
    list_n_col_to_delete = []
    for n_col in range(skip_cols, len_cols - 1):
        serie = df.iloc[:, n_col]
        # check for column with more than 1 unique value (folder root)
        col_has_one_unique_value = check_col_unique_values(serie)
        if col_has_one_unique_value:
            name_col = df.columns[n_col]
            list_n_col_to_delete.append(name_col)

    df = df.drop(list_n_col_to_delete, axis=1)

    return df


def include_cols_folders_structure(df):
    """
    Includes to the right of the DataFrame, columns corresponding to each
     depth level of the folder structure of the origin files
    :df: DataFrame. Requires column 'file_path_folder_origin'
    """

    skip_cols = len(df.columns)
    df_folder = utils_timestamp.explode_parts_serie_path(
        df["file_path_folder_origin"]
    )

    df_folder = df.merge(df_folder, left_index=True, right_index=True)
    # remove root folders columns (dont change along the files)
    df_folder = remove_root_folders(df_folder, skip_cols=skip_cols)
    return df_folder


def get_df_source(file_path_report_origin, list_columns_keep=None):
    def test_columns_video_details(df_source, list_columns_keep):
        # check if columns exists in dataframe
        list_known_items = df_source.columns
        return_test_unknown_items = utils_timestamp.test_unknown_items(
            list_items=list_columns_keep,
            list_known_items=list_known_items,
            name_test="required columns",
        )
        if return_test_unknown_items is False:
            logging.error(
                "Possible cause: Reencode step in script "
                + '"vidtool" may have been skipped by accident'
            )
            return False
        else:
            return True

    if utils_timestamp.test_file_close(file_path_report_origin) is False:
        return False

    df_source = pd.read_csv(file_path_report_origin)

    if list_columns_keep is None:
        list_columns_keep = [
            "file_path_folder",
            "file_name",
            "file_path_folder_origin",
            "file_name_origin",
            "file_output",
        ]

    if test_columns_video_details(df_source, list_columns_keep) is False:
        exit()

    # If there is a 'duration' column, add the list of columns to keep
    if "duration" in df_source.columns:
        list_columns_keep.append("duration")
    df = df_source.loc[:, list_columns_keep]

    return df


def get_duration_video(file_path):
    """using the ffmpeg lib, show the length of a video in seconds,
    excluding micro seconds

    Args:
        file_path (str): absolite video file path

    Returns:
        datetime: length of a video, excluding micro seconds
    """

    duration_sec = get_length(file_path)
    duration_delta = datetime.timedelta(seconds=duration_sec)

    # excluding micro seconds
    duration_delta_micro = datetime.timedelta(
        microseconds=duration_delta.microseconds
    )
    duration_format = duration_delta - duration_delta_micro

    return duration_format


def get_length(video_file_path):
    """from a absolute video file path, get duration in seconds. Using ffmpeg.

    Args:
        video_file_path (string): video file_path

    Returns:
        float: video duration in seconds
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_file_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    return float(result.stdout)


def timestamp_link_maker(
    folder_path_output: Path,
    file_path_report_origin: Path,
    start_index_number,
    hashtag_index: str = "Block",
    dict_summary={},
    descriptions_auto_adapt=True,
):
    """
    From spreadsheet video data, create timestamps, Generating 2 files:
        summary.txt: Containing a summary, adding all videos hashtags_link
                        grouped by name of the first level folders
        descriptions.csv: With columns: file_output, description, warning
    About required spreadsheet:
    - can be automatically generated by the app vidtool:
        https://github.com/apenasrr/vidtool

    - Required columns: ['file_path_folder', 'file_name',
                         'file_path_folder_origin',
                         'file_name_origin', 'file_output']
    - Optional columns: ['duration']

    Args:
        folder_path_output (str): Absolute path of the folder where
                                   the files are to be generated
        file_path_report_origin (str): absolute spreadsheet path.
        start_index_number (int): Initial index number at which the video
                                   summary and description should start
        dict_summary (dict, optional): file_path of txts with text to be insert
            on top and bottom of output file summary.txt. Defaults to {}.
            keys: [path_summary_top, path_summary_bot]
        descriptions_auto_adapt (bool, optional): (
            True for auto-adapt description to max length of 999 chars
        )
    """

    def add_column_filepath(df):
        df["file_path"] = df[["file_path_folder", "file_name"]].apply(
            lambda row: Path(*row), axis=1
        )

        return df

    def process_column_duration(df):
        """If there is a 'duration' column, it changes to timedelta format.
           If there is not a 'duration' column, create it in timedelta format.

        Args:
            df dataframe: video_details dataframe with column 'file_path'

        Returns:
            dataframe: Update dataframe with column 'duration'
                        in timedelta format
        """

        if "duration" in df.columns:
            df["duration"] = pd.to_timedelta(df["duration"])
        else:
            df["duration"] = df["file_path"].apply(get_duration_video)

        return df

    df = get_df_source(file_path_report_origin)
    if df is False:
        return False

    # TODO: check for essencials columns
    df = add_column_filepath(df)
    df = process_column_duration(df)

    df = include_timestamp(df)

    df = include_cols_folders_structure(df)

    # create descriptions.csv
    # # df_description = create_df_description_without_folder(df)
    df_description = create_df_description_with_folder(df)

    # # input hashtag to mark blocks
    df_description = description_implant_hashtag_blocks(
        df_description, hashtag_index, start_index_number
    )

    # # input signature in description bottom
    df_description = description_implant_signature_bottom(df=df_description)

    # save upload_plan.csv
    file_path_output = folder_path_output / "upload_plan.csv"
    df_description.to_csv(file_path_output, index=False)

    # Check if has warning
    has_warning = utils_timestamp.check_descriptions_warning_from_df(
        df_description
    )
    if has_warning:
        if descriptions_auto_adapt:
            df_description = utils_timestamp.adapt_description_to_limit(
                df_description
            )
            df_description.to_csv(file_path_output, index=False)
        else:
            print('\nThere are warnings in the file "upload_plan.csv"')

    # create summary.txt
    create_summary(
        file_path_report_origin,
        folder_path_output,
        start_index_number,
        dict_summary,
        hashtag_index,
    )

    # TODO: feature to expose folder hierarchies more than one level deep


def main():
    # get dict config_data
    folder_script_path_relative = Path(__file__).parent
    folder_script_path = folder_script_path_relative.absolute()
    file_path_config = folder_script_path / "config.ini"
    config_data = utils_timestamp.get_config_data(file_path_config)

    # set variables
    folder_path_output = Path(config_data["path_folder_output"])
    file_path_report = Path(config_data["path_file_report"])
    path_summary_top = config_data["path_summary_top"]
    path_summary_bot = config_data["path_summary_bot"]
    start_index = int(config_data["start_index"])
    hashtag_index = config_data["hashtag_index"]

    descriptions_auto_adapt_str = config_data["descriptions_auto_adapt"]
    if descriptions_auto_adapt_str == "true":
        descriptions_auto_adapt = True
    else:
        descriptions_auto_adapt = False

    dict_summary = {}
    dict_summary["path_summary_top"] = path_summary_top
    dict_summary["path_summary_bot"] = path_summary_bot

    # ensure folder_output existence
    utils_timestamp.ensure_folder_existence([folder_path_output])

    # TODO: ensure aux files existence
    timestamp_link_maker(
        folder_path_output,
        file_path_report,
        start_index,
        hashtag_index,
        dict_summary,
        descriptions_auto_adapt,
    )


# if __name__ == "__main__":
#     logging_config()
#     main()
