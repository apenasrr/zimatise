import logging
import os
import time
from pathlib import Path

import vidtool

import update_description_summary
import utils
import zimatise_monitor
from header_maker import header_maker
from timestamp_link_maker import timestamp_link_maker


def logging_config():
    logfilename = "log-" + "auto_report" + ".txt"
    logging.basicConfig(
        level=logging.DEBUG,
        format=" %(asctime)s-%(levelname)s-%(message)s",
        handlers=[logging.FileHandler(logfilename, "w", "utf-8")],
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(" %(asctime)s-%(levelname)s-%(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)


def show_projects_to_reencode(list_project_path):
    str_header = "AutoTimestamp - Build summary and timestamps\n"
    utils.show_projects_queue(str_header, list_project_path)


def process_auto_timestamp(project_path: Path):
    # define variables
    folder_script_path = utils.get_folder_script_path()
    path_file_config = folder_script_path / "config.ini"
    config = utils.get_config_data(path_file_config)
    hashtag_index = config["hashtag_index"]
    start_index = int(config["start_index"])
    path_summary_top = config["path_summary_top"]
    path_summary_bot = config["path_summary_bot"]
    document_hashtag = config["document_hashtag"]
    document_title = config["document_title"]
    dict_summary = {}
    dict_summary["path_summary_top"] = path_summary_top
    dict_summary["path_summary_bot"] = path_summary_bot

    folder_path_project_process = utils.get_folder_path_project_process(
        project_path
    )
    file_path_report = folder_path_project_process / "video_details.xlsx"
    folder_path_videos_encoded = folder_path_project_process / "videos_encoded"
    utils.ensure_folder_existence([folder_path_videos_encoded])

    try:
        # make descriptions.xlsx and summary.txt
        timestamp_link_maker(
            folder_path_output=folder_path_project_process,
            file_path_report_origin=file_path_report,
            hashtag_index=hashtag_index,
            start_index_number=start_index,
            dict_summary=dict_summary,
        )

        # make header project
        header_maker(folder_path_project_process)

        update_description_summary.main(
            path_summary_top,
            folder_path_project_process,
            document_hashtag,
            document_title,
        )
        return True
    except Exception as e:
        print(f"{e}\nAuto_Timestamp Error: {project_path}")
        return False


def main():
    # define flag to_report
    flag_rule = zimatise_monitor.get_flag_rule("to_timestamp")
    file_path_monitor = zimatise_monitor.get_file_path_monitor()

    while True:
        list_project_path = utils.get_list_project_to_process(
            file_path_monitor, flag_rule
        )
        utils.clean_cmd()
        show_projects_to_reencode(list_project_path)
        project_path = utils.select_a_project_to_process(list_project_path)
        if project_path == "":
            time.sleep(5)
            continue
        success = process_auto_timestamp(project_path)
        if success:
            # set stage 2_auto_zip
            zimatise_monitor.set_stage_project(
                project_path, stage_name="7_timestamp", stage_value=1
            )
        else:
            pass

        time.sleep(10)


if __name__ == "__main__":
    logging_config()
    main()
