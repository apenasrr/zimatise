import datetime
import os
import time
from pathlib import Path

import pandas as pd

import utils


def create_monitor(file_name_monitor):
    list_columns_order = [
        "dt_start",
        "project_name",
        "project_path",
        "1_start_auth",
        "2_auto_zip",
        "3_auto_report",
        "4_reencode_auth",
        "5_auto_reencode",
        "6_auto_join",
        "7_timestamp",
        "8_auto_send_auth",
        "9_uploaded",
        "dt_upload",
        "chat_link",
    ]

    df_monitor = pd.DataFrame(columns=list_columns_order)
    df_monitor.to_csv(file_name_monitor, index=False)


def ensure_exists_monitor(file_name_monitor):
    exist = Path(file_name_monitor).exists()
    if not exist:
        create_monitor(file_name_monitor)


def check_folders_auth(list_folder_path):
    list_ = []
    for folder_path in list_folder_path:
        folder_name = Path(folder_path).name
        if folder_name[0] == "_":
            list_.append(folder_path)
    return list_


def get_list_folder_path_start_auth(folder_path_start: Path):
    if folder_path_start.exists() is False:
        folder_path_start.mkdir(exist_ok=True)
        return []

    list_folder_name = os.listdir(folder_path_start)
    list_folder_path = []
    for folder_name in list_folder_name:
        folder_path = folder_path_start / folder_name
        list_folder_path.append(str(folder_path))

    list_folder_path_start_auth = check_folders_auth(list_folder_path)
    return list_folder_path_start_auth


def check_project_in_monitor(folder_path_project: str, file_path_monitor: str):
    """verifies that folder_path are in the monitor

    Args:
        folder_path_project (str):
        file_path_monitor (str):

    Returns:
        boolean: true if folder_path exist in monitor
    """

    df = pd.read_csv(file_path_monitor)
    serie_boolean = df["project_path"].isin([folder_path_project])
    exist = any(serie_boolean)

    return exist


def add_project_in_monitor(folder_path_project: Path, file_path_monitor: Path):
    # set variables
    dt_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folder_name_project_raw = folder_path_project.name
    folder_name_project = folder_name_project_raw.strip("_")

    # open monitor report
    df = pd.read_csv(file_path_monitor)

    # add project
    new_line = [
        dt_start,
        folder_name_project,
        folder_path_project,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        "",
        "",
    ]
    df = df.append(pd.Series(new_line, index=df.columns), ignore_index=True)

    # save monitor report
    df.to_csv(file_path_monitor, index=False)


def get_flag_rule(flag_name: str) -> dict:
    was_started = {"1_start_auth": 1}
    to_zip = {"1_start_auth": 1, "2_auto_zip": 0}
    to_report = {"1_start_auth": 1, "3_auto_report": 0}
    auth_encode = {"3_auto_report": 1, "4_reencode_auth": 0}
    to_encode = {"4_reencode_auth": 1, "5_auto_reencode": 0}
    to_join = {"5_auto_reencode": 1, "6_auto_join": 0}
    to_timestamp = {"6_auto_join": 1, "7_timestamp": 0}
    fix_desc = {"7_timestamp": 1, "8_auto_send_auth": 0}

    flag_rules = {
        "was_started": was_started,
        "to_zip": to_zip,
        "to_report": to_report,
        "auth_encode": auth_encode,
        "to_encode": to_encode,
        "to_join": to_join,
        "to_timestamp": to_timestamp,
        "fix_desc": fix_desc,
    }
    return flag_rules[flag_name]


def process_flag_project(flag_rule: dict) -> bool:
    # load dataframe
    file_path_monitor = get_file_path_monitor()
    df = pd.read_csv(file_path_monitor)

    # filter flag for project
    # fmt: off
    list_serie_boolean = \
        utils.get_series_boolean_by_df_filter(df, dict_=flag_rule)

    mask = utils.serie_boolean_mult_list(list_serie_boolean)

    # return if exist
    exist = any(mask)
    return exist


def check_flag_project(folder_path_project, flag_name):
    dict_flag_rule = get_flag_rule(flag_name)
    dict_flag_rule["project_path"] = folder_path_project
    flag_status = process_flag_project(flag_rule=dict_flag_rule)
    return flag_status


def check_unique_project_line(serie_boolean):
    count_found = sum(serie_boolean)
    if count_found != 1:
        raise ValueError("Multiple lines of the same project was found.")
    elif count_found == 0:
        raise ValueError("No line of this project was found.")


def set_stage_project(
    folder_path_project: str, stage_name: str, stage_value: int
):
    # load dataframe
    file_path_monitor = get_file_path_monitor()
    df = pd.read_csv(file_path_monitor)

    # filter project
    serie_boolean = df["project_path"].isin([folder_path_project])

    # check unique
    check_unique_project_line(serie_boolean)

    # set stage
    df.loc[serie_boolean, stage_name] = stage_value

    # update and save report monitor
    update_monitor(df)


def get_hit_max_path(return_test_max_path):
    test_approved = return_test_max_path["result"]
    hit_max_path = not test_approved
    return hit_max_path


def get_list_file_path_long(return_test_max_path):
    list_file_path_long = return_test_max_path["list_file_path_long"]
    return list_file_path_long


def ask_correct_or_jump(
    folder_path_project: str, list_file_path_long: list
) -> bool:
    """ask to test again or skip project

    Args:
        folder_path_project (str): project folder_path
        list_file_path_long (list): list of file_path who has path_lenght above max_path

    Returns:
        bool: True if choose skip
    """

    msg_project_header = f"\nProject: {folder_path_project}\n"

    question = (
        "\nThis files are with MAX_PATH above the limit allowed.\n"
        + "Edit the name of folders and files to reduce its lenght.\n\n"
        + "1 - Test again (default)\n"
        + "2 - Skip project\n\n"
    )

    print(msg_project_header)
    for file_path_long in list_file_path_long:
        print("- " + file_path_long)

    print(question)
    answer = input("Choose an option: ")
    if answer == "" or answer == "1":
        choose_jump = False
        return choose_jump
    else:
        choose_jump = True
        return choose_jump


def set_project_as_unauth(folder_path_project: Path):
    folder_root = folder_path_project.parent
    folder_name = folder_path_project.name
    folder_name_unauth = folder_name.strip("_")
    folder_path_unauth = folder_root / folder_name_unauth
    # rename folder to unauthorized
    while True:
        try:
            folder_path_project.rename(folder_path_unauth)
            return
        except Exception as e:
            print(
                f"{e}\n Error renaming the Project {folder_name}.\n"
                + "Close the files of this project.\n"
                + "Press [Enter] to try again."
            )


def update_monitor(df):
    file_path_monitor = get_file_path_monitor()
    while True:
        try:
            df.to_csv(file_path_monitor, index=False)
            return
        except Exception as e:
            print(
                f"\n{e}\nCould not edit the monitor file.\n"
                + "Verify that any software is using it and close.\n"
            )
            input("Type [Enter] to try again.")


def check_and_add_new_project(
    folder_path_project, file_path_monitor, max_path
):
    """
    Check if the project files respect MAX_PATH
    and authorize to start the process flow
    Details:
        - Verifies if Project_Path is on the monitor
                - if there is
                        - If project has already started, skip
            - If project has not started, make Max_Path tests
                                - if pass, mark to the next stage. 1_start_auth
                                - if dont, require fix or skip
                    - if skip, unauthorizes project so that it is no longer
                        seen by the monitor
                - If there is not have, add project on the monitor
    """

    # verifica se folder_path contém no relatório
    project_in_monitor = check_project_in_monitor(
        folder_path_project, file_path_monitor
    )
    if project_in_monitor:
        print("-= Zimatise - Projects Monitor =-")
        # check_project_was_started
        project_was_started = check_flag_project(
            folder_path_project, flag_name="was_started"
        )

        if project_was_started:
            return
        else:
            while True:
                # seek start_auth
                # # test_max_path
                # fmt: off
                return_test_max_path = \
                    utils.test_folder_has_file_path_long(folder_path_project,
                                                         max_path)
                hit_max_path = get_hit_max_path(return_test_max_path)
                if hit_max_path:
                    # fmt: off
                    list_file_path_long = \
                        get_list_file_path_long(return_test_max_path)

                    choose_jump = ask_correct_or_jump(
                        folder_path_project, list_file_path_long
                    )
                    if choose_jump:
                        # set project as unauthorized.
                        # Remove from folder_name, initial underline
                        set_project_as_unauth(folder_path_project)
                        return
                    else:  # choose Correct and test again
                        # clean terminal
                        utils.clean_cmd()
                        continue  # repeats loop
                else:
                    # auth the project to the next stage - 1_start_auth
                    # fmt: off
                    set_stage_project(folder_path_project,
                                      stage_name="1_start_auth",
                                      stage_value=1)
                    return

    else:
        # add folder_path in monitor
        add_project_in_monitor(folder_path_project, file_path_monitor)


def get_file_path_monitor():
    file_path_monitor = "report_monitor.csv"
    return file_path_monitor


def confirm_reencode_auth(folder_path_project):
    need_auth_to_reencode = check_flag_project(
        folder_path_project, flag_name="auth_encode"
    )

    if need_auth_to_reencode:
        choose_jump = ask_reencode_or_jump(folder_path_project)
        if choose_jump:
            return
        else:
            # auth project to reencode - 4_reencode_auth
            # fmt: off
            set_stage_project(folder_path_project,
                              stage_name="4_reencode_auth",
                              stage_value=1)


def ask_reencode_or_jump(folder_path_project: str) -> bool:
    """ask to auth reencode or skip project

    Args:
        folder_path_project (str): project folder_path
    Returns:
        bool: True if choose skip
    """

    msg_project_header = f"\nProject: {folder_path_project}\n"

    question = (
        "\nThe project requires authorization for reencode.\n"
        + "If necessary, change the reencode plan in the column "
        + '"video_resolution_to_change".\n\n'
        + "1 - Confirm (default)\n"
        + "2 - Skip project\n\n"
    )

    print(msg_project_header)
    print(question)
    answer = input("Choose an option: ")

    if answer == "" or answer == "1":
        return False
    else:
        return True


def main():
    folder_script_path = utils.get_folder_script_path()
    path_file_config = folder_script_path / "config.ini"
    config = utils.get_config_data(path_file_config)
    folder_path_start = config["folder_path_start"]
    max_path = int(config["max_path"])
    file_path_monitor = get_file_path_monitor()
    time_loop_freq_sec = 10
    ensure_exists_monitor(file_path_monitor)

    while True:
        # fmt: off
        list_folder_path_start_auth = \
            get_list_folder_path_start_auth(folder_path_start)

        for folder_path_project in list_folder_path_start_auth:

            # possible max_path correction
            # fmt: off
            check_and_add_new_project(folder_path_project,
                                      file_path_monitor,
                                      max_path)

            confirm_reencode_auth(folder_path_project)
            utils.clean_cmd()

        time.sleep(time_loop_freq_sec)

    # 6_auto_join, 7_timestamp, 8_auto_send_auth, 8_uploaded, dt_upload, chat_link

    # TODO:
    # - 7_ true, 8_false - solicita tratamento de estouro de limite da descricao - eventual


if __name__ == "__main__":
    main()
