"""
    Create by: apenasrr
    Source: https://github.com/apenasrr/zimatise

    Workflow for automatic processing of aggregated videos, construction of
    timestamps and posting with dynamic summary
    A process aggregator that uses independent solutions

    ZI pind
    MA ss_videojoin
    TI mestamp
    SE nd_files

    Requirements:
    -https://github.com/apenasrr/zipind
    -https://github.com/apenasrr/vidtool
    -https://github.com/apenasrr/tgsender

    ## How to use (for windows users)
    - Enter the 'zimatise' folder
    - Execute `_install.bat` to create the virtual environment and install the dependencies
    - Run the file `zimatise_one.bat`
    - Follow the on-screen instructions


    We recommend:
    mises.org - Educate yourself about economic and political freedom
    lbry.tv - Store files and videos on blockchain ensuring free speech
    https://www.activism.net/cypherpunk/manifesto.html -  How encryption is essential to Free Speech and Privacy
"""

from __future__ import annotations

import logging
import os
import shutil
import time
from pathlib import Path
from typing import List

import vidtool
import zipind
from tgsender import tgsender

import autopost_summary
import moc
import project_metadata
import update_description_summary
import utils
from description import single_mode
from header_maker import header_maker
from timestamp_link_maker import timestamp_link_maker, utils_timestamp


def logging_config():
    logfilename = "log-" + "zimatise" + ".txt"
    logging.basicConfig(
        level=logging.INFO,
        format=" %(asctime)s-%(levelname)s-%(message)s",
        handlers=[logging.FileHandler(logfilename, "w", "utf-8")],
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    # set a format which is simpler for console use
    formatter = logging.Formatter(" %(asctime)s-%(levelname)s-%(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)


def menu_ask():
    print("1-Create independent Zip parts for not_video_files")
    print("2-Generate worksheet listing the files")
    print(
        "3-Process reencode of videos marked in column "
        '"video_resolution_to_change"'
    )
    print("4-Group videos with the same codec and resolution")
    print("5-Make Timestamps and Descriptions report")
    print("6-Auto-send to Telegram")

    msg_type_answer = "Type your answer: "
    make_report = int(input(f"\n{msg_type_answer}"))
    if make_report == 1:
        return 1
    elif make_report == 2:
        return 2
    elif make_report == 3:
        return 3
    elif make_report == 4:
        return 4
    elif make_report == 5:
        return 5
    elif make_report == 6:
        return 6
    else:
        msg_invalid_option = "Invalid option"
        raise msg_invalid_option


def play_sound():
    file_path_sound = ""
    os.system(f'start wmplayer "{file_path_sound}"')


def define_mb_per_file(file_path_config, file_size_limit_mb):
    if file_size_limit_mb is not None:
        repeat_size = input(
            f"Define limit of {file_size_limit_mb} " + "MB per file? y/n\n"
        )
        if repeat_size == "n":
            file_size_limit_mb = zipind.zipind.ask_mb_file()
            zipind.zipind.config_update_data(
                file_path_config, "file_size_limit_mb", str(file_size_limit_mb)
            )
    else:
        file_size_limit_mb = zipind.zipind.ask_mb_file()
        zipind.zipind.config_update_data(
            file_path_config, "file_size_limit_mb", str(file_size_limit_mb)
        )
    return file_size_limit_mb


def send_to_moc(
    send_moc,
    list_moc_chat_id,
    template_moc,
    folder_path_report,
    folder_path_project,
):
    if send_moc == 1:
        moc.pipe_publish(
            list_moc_chat_id,
            template_moc,
            folder_path_report,
            folder_path_project,
        )


def clean_temp_files(autodel_video_temp, folder_path_project: Path):
    list_folder_name_to_delete = [
        "output_videos",
        "videos_encoded",
        "videos_splitted",
    ]
    if autodel_video_temp != 1:
        return

    for folder_name_to_delete in list_folder_name_to_delete:
        folder_path_to_delete = folder_path_project / folder_name_to_delete
        if folder_path_to_delete.exists():
            shutil.rmtree(str(folder_path_to_delete), ignore_errors=True)
        else:
            pass


def run(
    folder_path_project: Path,
    file_path_report: Path,
    list_video_extensions,
    file_size_limit_mb,
    duration_limit,
    start_index,
    activate_transition,
    hashtag_index,
    dict_summary,
    descriptions_auto_adapt,
    path_summary_top: Path,
    document_hashtag,
    document_title,
    register_invite_link,
    reencode_plan,
    mode,
    send_moc,
    list_moc_chat_id,
    autodel_video_temp,
):
    folder_path_project = vidtool.get_folder_path(folder_path_project)
    folder_path_report = file_path_report.parent
    print(f"Project: {folder_path_project.name}\n\n")
    folder_path_output = folder_path_report / "output_videos"

    ################################### p1
    utils.ensure_folder_existence([folder_path_output])
    zipind.zipind_core.run(
        path_folder=str(folder_path_project),
        mb_per_file=file_size_limit_mb,
        path_folder_output=str(folder_path_output),
        mode=mode,
        ignore_extensions=list_video_extensions,
    )

    ################################### p2
    vidtool.step_create_report_filled(
        folder_path_project,
        file_path_report,
        list_video_extensions,
        reencode_plan,
    )
    ################################### p3
    folder_path_videos_encoded = vidtool.set_path_folder_videos_encoded(
        folder_path_project
    )
    vidtool.ensure_folder_existence([str(folder_path_videos_encoded)])

    # reencode videos mark in column video_resolution_to_change
    vidtool.set_make_reencode(
        str(file_path_report), str(folder_path_videos_encoded)
    )

    ################################### p4
    folder_path_videos_splitted = vidtool.set_path_folder_videos_splitted(
        folder_path_project
    )

    vidtool.ensure_folder_existence([str(folder_path_videos_splitted)])

    folder_path_videos_joined = vidtool.set_path_folder_videos_joined(
        folder_path_project
    )

    vidtool.ensure_folder_existence([str(folder_path_videos_joined)])

    filename_output = vidtool.get_folder_name_normalized(folder_path_project)

    folder_path_videos_cache = vidtool.set_path_folder_videos_cache(
        folder_path_project
    )

    vidtool.ensure_folder_existence([str(folder_path_videos_cache)])

    if reencode_plan == "group":
        # Fill group_column.
        #  Establishes separation criteria for the join videos step
        vidtool.set_group_column(str(file_path_report))

    # split videos too big
    vidtool.set_split_videos(
        str(file_path_report),
        file_size_limit_mb,
        str(folder_path_videos_splitted),
        duration_limit,
    )

    if reencode_plan == "group":
        # join all videos
        vidtool.set_join_videos(
            str(file_path_report),
            file_size_limit_mb,
            filename_output,
            str(folder_path_videos_joined),
            str(folder_path_videos_cache),
            duration_limit,
            start_index,
            activate_transition,
        )

    ################################### p5

    if reencode_plan == "group":
        # make descriptions.xlsx and summary.txt
        timestamp_link_maker(
            folder_path_output=folder_path_report,
            file_path_report_origin=file_path_report,
            hashtag_index=hashtag_index,
            start_index_number=start_index,
            dict_summary=dict_summary,
            descriptions_auto_adapt=descriptions_auto_adapt,
        )

        update_description_summary.main(
            path_summary_top,
            folder_path_report,
            document_hashtag,
            document_title,
        )
    else:
        # create descriptions.xlsx for single reencode
        single_mode.single_description_summary(
            folder_path_output=folder_path_report,
            file_path_report_origin=file_path_report,
            dict_summary=dict_summary,
        )

        update_description_summary.main(
            path_summary_top,
            folder_path_report,
            document_hashtag,
            document_title,
        )

    # make header project
    header_maker(folder_path_report, folder_path_project)

    # Check if has warnings
    has_warning = utils_timestamp.check_descriptions_warning(
        folder_path_report
    )
    if has_warning:
        input(
            '\nThere are warnings in the file "descriptions.xlsx".'
            + "Correct before the next step."
        )
    else:
        pass

    ################################### p6

    folder_script_path = utils.get_folder_script_path()
    file_path_config = folder_script_path / "config.ini"
    config = utils.get_config_data(file_path_config)
    dict_config = config

    tgsender.send_via_telegram_api(Path(folder_path_report), dict_config)

    # Post and Pin summary
    autopost_summary.run(folder_path_report)

    # Register invite_link
    if register_invite_link == "1":
        project_metadata.include(folder_path_project, folder_path_report)

    # Publish on moc
    file_path_moc_template = Path("user") / "moc_template.txt"
    send_to_moc(
        send_moc,
        list_moc_chat_id,
        file_path_moc_template,
        folder_path_report,
        folder_path_project,
    )

    clean_temp_files(autodel_video_temp, folder_path_report)


def get_list_internal_folder_path(root_folder_path: Path) -> List[Path]:

    return [x for x in root_folder_path.iterdir() if x.is_dir()]


def get_folder_path_uploaded(folder_path):
    if Path(folder_path).exists():
        return folder_path
    else:
        folder_path_uploaded = Path(".").absolute() / "uploaded"
        folder_path_uploaded.mkdir()
        return folder_path_uploaded


def get_list_chat_id(param_chat_id: str) -> list:
    """Converts string parameter with 1 or more chat_id to chat_id list

    Args:
        param_chat_id (str): parameter with 1 or more chat_id separated by
        comma

    Raises:
        Exception: If the chat_id is invalid because it is not numerical

    Returns:
        list: chat_id list
    """

    list_param_moc_chat_id = [x.strip() for x in param_chat_id.split(",")]
    list_chat_id = []
    for moc_chat_id in list_param_moc_chat_id:
        try:
            list_chat_id.append(int(moc_chat_id))
        except Exception:
            raise Exception(f"moc_chat_id invalid. - {moc_chat_id}")
    return list_chat_id


def main():
    """
    How to use
    Checkout the repo: https://github.com/apenasrr/zimatise
    """

    # get config data
    folder_script_path = utils.get_folder_script_path()
    file_path_config = Path(folder_script_path) / "config.ini"
    config = utils.get_config_data(file_path_config)
    folder_path_start = Path(config["folder_path_start"])
    file_size_limit_mb = int(config["file_size_limit_mb"])
    mode = config["mode"]
    list_video_extensions = config["video_extensions"].split(",")
    duration_limit = config["duration_limit"]
    activate_transition = config["activate_transition"]
    start_index = int(config["start_index"])
    hashtag_index = config["hashtag_index"]
    reencode_plan = config["reencode_plan"]
    send_moc = int(config["send_moc"])
    list_moc_chat_id = get_list_chat_id(config["moc_chat_id"])
    autodel_video_temp = int(config["autodel_video_temp"])

    descriptions_auto_adapt_str = config["descriptions_auto_adapt"]
    if descriptions_auto_adapt_str == "true":
        descriptions_auto_adapt = True
    else:
        descriptions_auto_adapt = False

    path_summary_top = Path("user") / config["path_summary_top"]
    path_summary_bot = Path("user") / config["path_summary_bot"]
    document_hashtag = config["document_hashtag"]
    document_title = config["document_title"]

    dict_summary = {}
    dict_summary["path_summary_top"] = path_summary_top
    dict_summary["path_summary_bot"] = path_summary_bot
    register_invite_link = config["register_invite_link"]

    file_path_report = None
    folder_path_project = None
    utils.ensure_folder_existence([Path("projects")])

    while True:
        print("Monitoring folder: ", str(folder_path_start), "\n")
        list_project_path = get_list_internal_folder_path(folder_path_start)
        if len(list_project_path) == 0:
            time.sleep(5)
            vidtool.clean_cmd()
            continue

        folder_path_project = list_project_path[0]
        file_path_report = vidtool.set_path_file_report(
            Path(folder_path_project)
        )
        run(
            folder_path_project,
            file_path_report,
            list_video_extensions,
            file_size_limit_mb,
            duration_limit,
            start_index,
            activate_transition,
            hashtag_index,
            dict_summary,
            descriptions_auto_adapt,
            path_summary_top,
            document_hashtag,
            document_title,
            register_invite_link,
            reencode_plan,
            mode,
            send_moc,
            list_moc_chat_id,
            autodel_video_temp,
        )

        vidtool.clean_cmd()
        utils.move_project(folder_path_project, config)


if __name__ == "__main__":
    logging_config()
    main()
