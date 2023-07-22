import logging
import time
from pathlib import Path

import vidtool

import utils
import zimatise_monitor


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
    str_header = "AutoReencode - Reencode videos from report plan\n"
    utils.show_projects_queue(str_header, list_project_path)


def process_auto_reencode(project_path: Path):
    # define variables
    folder_path_project_process = utils.get_folder_path_project_process(
        project_path
    )
    file_path_report = folder_path_project_process / "video_details.xlsx"
    folder_path_videos_encoded = folder_path_project_process / "videos_encoded"
    utils.ensure_folder_existence([folder_path_videos_encoded])

    try:
        vidtool.set_make_reencode(file_path_report, folder_path_videos_encoded)
        vidtool.set_correct_duration(file_path_report)
        return True
    except Exception as e:
        print(f"{e}\nAuto_Reencode Error: {project_path}")
        return False


def main():
    # define flag to_report
    flag_rule = zimatise_monitor.get_flag_rule("to_encode")
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
        success = process_auto_reencode(project_path)
        if success:
            # set stage 2_auto_zip
            zimatise_monitor.set_stage_project(
                project_path, stage_name="5_auto_reencode", stage_value=1
            )
        else:
            pass

        time.sleep(10)


if __name__ == "__main__":
    logging_config()
    main()
