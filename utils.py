import logging
import os
import sys
from configparser import ConfigParser
from pathlib import Path
from typing import List

import pandas as pd
import vidtool


def move_project(folder_path_project: Path, config_data: dict):
    move_to_uploaded = config_data.get("move_to_uploaded", "0")
    folder_path_uploaded = Path(config_data.get("folder_path_uploaded"))

    if (
        not folder_path_uploaded
        or not folder_path_project.exists()
        or move_to_uploaded == "0"
    ):
        return

    project_path_uploaded = folder_path_uploaded / folder_path_project.name
    folder_path_project.rename(project_path_uploaded)

    folder_path_auth = project_path_uploaded.parent / (
        "_" + project_path_uploaded.name
    )
    project_path_uploaded.rename(folder_path_auth)


def add_path_script_folders(list_folders_name: List[str]):
    list_repo_dont_found = []
    for folder_name in list_folders_name:
        active_folder_path = Path(__file__).absolute().parent
        script_folder_path = active_folder_path.parent / folder_name

        if script_folder_path.exists():
            sys.path.append(str(script_folder_path))
        else:
            list_repo_dont_found.append(str(script_folder_path))

    # alert in case of not found repositories
    qt_not_found = len(list_repo_dont_found)
    if qt_not_found != 0:
        if qt_not_found > 1:
            repo = "repositories"
        else:
            repo = "repository"
        str_list_repo_dont_found = "\n".join(list_repo_dont_found)
        logging.error(
            f"The {repo} below could not be found. "
            + "Make sure it exists with the proper folder "
            + f"name.\n{str_list_repo_dont_found}\n"
        )
        exit()


def show_projects_queue(header, list_project_path: List[Path]):
    print(header)
    if list_project_path[0] == "":
        print("Awaiting a new task...")
    else:
        for project_path in list_project_path:
            folder_name = project_path.name
            print(f"-{folder_name}")
        print("")


def get_list_project_to_process(file_path_monitor, flag_rule):
    df = pd.read_csv(file_path_monitor)

    list_serie_boolean = get_series_boolean_by_df_filter(df, dict_=flag_rule)
    mask = serie_boolean_mult_list(list_serie_boolean)
    if sum(mask) == 0:
        list_project_path_to_process = [""]
    else:
        serie_project_path_to_zip = df.loc[mask, "project_path"]
        list_project_path_to_process = serie_project_path_to_zip.to_list()

    return list_project_path_to_process


def select_a_project_to_process(list_project_path: List[str]):
    project_to_process = list_project_path[0]
    return Path(project_to_process)


def serie_boolean_mult_list(list_serie_boolean):
    """Multiply a list of Boolean series

    Args:
        list_serie_boolean (list[serie]): list of boolean serie with same shape

    Returns:
        serie: serie resulting from operator '&'.
            e.g.: seri1 & serie2 & ... & serieN
    """

    df = pd.concat(list_serie_boolean, axis=1)
    serie_result = df.transpose().all()
    return serie_result


def get_series_boolean_by_df_filter(df, dict_):
    """filter a dataframe by a dict of 'column: value' pair,
        returning a list of boolean series

    Args:
        df (dataframe): origin dataframe
        dict_ (dict):
            dict with pairs: {columns1: value1, ..., columnsX: valueX}

    Returns:
        list[series]:
            list of boolean series representing filter result.
            A series for each column filtered.
    """

    list_serie_boolean = []
    for column, status in dict_.items():
        serie_boolean = df[column].isin([status])
        list_serie_boolean.append(serie_boolean)
    return list_serie_boolean


def clean_cmd():
    os.system("cls")


def get_folder_path_project_process(project_path: Path):
    folder_name_normalized = vidtool.get_folder_name_normalized(
        str(project_path)
    )

    folder_path_output_relative = "output_" + folder_name_normalized.strip("_")
    ensure_folder_existence([Path("projects")])

    folder_path_project_process = (
        Path("projects") / folder_path_output_relative
    )
    ensure_folder_existence([folder_path_project_process])
    return folder_path_project_process


def get_folder_path_project_output(folder_path_project_process: Path):
    folder_path_project_output = folder_path_project_process / "output_videos"
    ensure_folder_existence([folder_path_project_output])
    return folder_path_project_output


def test_folder_has_file_path_long(folder_path: Path, max_path=260):
    """Test if a folder has any file with file_path too long

    Args:
        folder_path (string):
    return:
        dict: keys: {result: bol, list_file_path_long: list}
    """

    list_file_path_long = []
    return_dict = {}
    return_dict["result"] = True

    for root, _, files in os.walk(str(folder_path)):
        for file in files:
            file_path = Path(root) / file
            len_file_path = len(str(file_path))
            if len_file_path > max_path:
                list_file_path_long.append(str(file_path))

    if len(list_file_path_long) != 0:
        return_dict["result"] = False

    return_dict["list_file_path_long"] = list_file_path_long
    return return_dict


def test_folders_has_path_long(list_folder_path: List[Path], max_path=260):
    """tests a serie of folders if any of them has files whose pathfile
    has a larger length than stipulated in max_path

    Args:
        list_folder_path (list): list of folder_path to be tested
        max_path (int, optional): max file_path len permitted. Defaults to 260.

    Returns:
        dict: {'approved': ['folder_path': folder_path, 'list_file_path_long': []],
               'rejected': ['folder_path': folder_path, 'list_file_path_long': list_file_path_long]}

    """

    result_test_max_path = {}
    list_folder_path_approved = []
    list_folder_path_rejected = []

    for folder_path in list_folder_path:
        dict_result_test_file_path_long = test_folder_has_file_path_long(
            folder_path, max_path
        )
        dict_folders_path = {}
        dict_folders_path["folder_path"] = str(folder_path)

        dict_folders_path[
            "list_file_path_long"
        ] = dict_result_test_file_path_long["list_file_path_long"]

        if dict_result_test_file_path_long["result"]:
            list_folder_path_approved.append(dict_folders_path)
        else:
            list_folder_path_rejected.append(dict_folders_path)
    result_test_max_path["approved"] = list_folder_path_approved
    result_test_max_path["rejected"] = list_folder_path_rejected
    return result_test_max_path


def get_folder_script_path() -> Path:
    folder_script_path_relative = Path(__file__).parent
    folder_script_path = folder_script_path_relative.absolute()

    return folder_script_path


def get_config_data(file_path_config: Path):
    """get default configuration data from file config.ini

    Returns:
        dict: config data
    """

    config_file = ConfigParser()
    config_file.read(file_path_config)
    default_config = dict(config_file["default"])
    return default_config


def ensure_folder_existence(folders_path: List[Path]):
    """
    :input: folders_path: List[Path]
    """

    for folder_path in folders_path:
        folder_path.mkdir(exist_ok=True)


def get_txt_content(file_path: Path):
    list_encode = ["utf-8-sig", "ISO-8859-1"]  # utf8, ansi
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
    raise Exception("encode", f"Cannot open file: {str(file_path)}")


def create_txt(file_path: Path, stringa: str):
    f = open(file_path, "w", encoding="utf8")
    f.write(stringa)
    f.close()


def format_time_delta(time_delta):
    days = time_delta.days
    totalSeconds = time_delta.seconds
    hours, remainder = divmod(totalSeconds, 3600)
    minutes, _ = divmod(remainder, 60)

    hours = days * 24 + hours
    return f"{hours}h {minutes}min"


def compile_template(d_keys, template_content):
    for key in d_keys.keys():
        template_content = template_content.replace(
            "{" + key + "}", d_keys[key]
        )

    output_content = template_content
    return output_content
