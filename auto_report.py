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


def show_projects_to_make_report(list_project_path):
    str_header = "AutoReport - Build a video metadata report\n"
    utils.show_projects_queue(str_header, list_project_path)


def process_make_report(project_path: Path):
    # define variables
    folder_script_path = utils.get_folder_script_path()
    path_file_config = folder_script_path / "config.ini"
    config = utils.get_config_data(path_file_config)
    list_video_extensions = config["video_extensions"].split(",")
    folder_path_project_process = utils.get_folder_path_project_process(
        project_path
    )

    file_path_report = folder_path_project_process / "video_details.xlsx"

    try:
        vidtool.step_create_report_filled(
            project_path, file_path_report, list_video_extensions
        )

        return True
    except Exception as e:
        print(f"{e}\nMake_Report Error: {project_path}")
        return False


def main():
    # define flag to_report
    flag_rule = zimatise_monitor.get_flag_rule("to_report")
    file_path_monitor = zimatise_monitor.get_file_path_monitor()

    while True:
        list_project_path = utils.get_list_project_to_process(
            file_path_monitor, flag_rule
        )
        utils.clean_cmd()
        show_projects_to_make_report(list_project_path)
        project_path = utils.select_a_project_to_process(list_project_path)
        if project_path == "":
            time.sleep(5)
            continue
        success = process_make_report(project_path)
        if success:
            # set stage 2_auto_zip
            zimatise_monitor.set_stage_project(
                project_path, stage_name="3_auto_report", stage_value=1
            )
        else:
            pass

        time.sleep(10)


if __name__ == "__main__":
    logging_config()
    main()
