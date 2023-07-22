import logging
import os
import time

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


def show_projects_to_join(list_project_path):
    str_header = "AutoJoin - Join videos without reencode from report plan\n"
    utils.show_projects_queue(str_header, list_project_path)


def process_auto_join(project_path: Path):
    # define variables
    folder_script_path = utils.get_folder_script_path()
    path_file_config = folder_script_path / "config.ini"
    config = utils.get_config_data(path_file_config)
    file_size_limit_mb = int(config["file_size_limit_mb"])
    duration_limit = config["duration_limit"]
    start_index = int(config["start_index"])
    activate_transition = config["activate_transition"]

    folder_path_project_process = utils.get_folder_path_project_process(
        project_path
    )
    file_path_report = folder_path_project_process / "video_details.xlsx"

    print(f"folder_path_project_process: {folder_path_project_process}")
    folder_path_videos_splitted = (
        folder_path_project_process / "videos_splitted"
    )
    utils.ensure_folder_existence([folder_path_videos_splitted])

    folder_path_videos_joined = utils.get_folder_path_project_output(
        folder_path_project_process
    )
    utils.ensure_folder_existence([folder_path_videos_joined])

    filename_output = vidtool.get_folder_name_normalized(project_path)

    folder_path_videos_cache = folder_path_project_process / "cache"
    utils.ensure_folder_existence([folder_path_videos_cache])

    try:
        # Fill group_column.
        #  Establishes separation criteria for the join videos step
        vidtool.set_group_column(file_path_report)

        # split videos too big
        vidtool.set_split_videos(
            file_path_report,
            file_size_limit_mb,
            folder_path_videos_splitted,
            duration_limit,
        )
        # join all videos
        vidtool.set_join_videos(
            file_path_report,
            file_size_limit_mb,
            filename_output,
            folder_path_videos_joined,
            folder_path_videos_cache,
            duration_limit,
            start_index,
            activate_transition,
        )
        return True
    except Exception as e:
        print(f"{e}\nAuto_Join Error: {project_path}")
        return False


def main():
    # define flag to_report
    flag_rule = zimatise_monitor.get_flag_rule("to_join")
    file_path_monitor = zimatise_monitor.get_file_path_monitor()

    while True:
        list_project_path = utils.get_list_project_to_process(
            file_path_monitor, flag_rule
        )
        utils.clean_cmd()
        show_projects_to_join(list_project_path)
        project_path = utils.select_a_project_to_process(list_project_path)
        if project_path == "":
            time.sleep(5)
            continue
        success = process_auto_join(project_path)
        if success:
            # set stage 2_auto_zip
            zimatise_monitor.set_stage_project(
                project_path, stage_name="6_auto_join", stage_value=1
            )
        else:
            pass

        time.sleep(10)


if __name__ == "__main__":
    logging_config()
    main()
