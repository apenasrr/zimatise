import logging
import time

import zipind

import utils
import zimatise_monitor


def logging_config():
    logfilename = "log-" + "auto_zip" + ".txt"
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


def process_zipind(project_path):
    # define variables
    folder_script_path = utils.get_folder_script_path()
    path_file_config = folder_script_path / "config.ini"
    config = utils.get_config_data(path_file_config)
    file_size_limit_mb = int(config["file_size_limit_mb"])
    mode = config["mode"]
    list_video_extensions = config["video_extensions"].split(",")
    folder_path_project_process = utils.get_folder_path_project_process(
        project_path
    )
    folder_path_project_output = utils.get_folder_path_project_output(
        folder_path_project_process
    )

    try:
        zipind.zipind_core.run(
            path_folder=project_path,
            mb_per_file=file_size_limit_mb,
            path_folder_output=folder_path_project_output,
            mode=mode,
            ignore_extensions=list_video_extensions,
        )
        return True
    except Exception as e:
        print(f"{e}\nZipind Error: {project_path}")
        return False


def show_projects_to_zip(list_project_path):
    str_header = (
        "Zipind - From a folder, "
        + "make a splited ZIP with INDependent parts\n"
    )
    utils.show_projects_queue(str_header, list_project_path)


def main():
    # define flag to_zip
    # # 1_start_auth=1, 2_auto_zip=0
    flag_rule = zimatise_monitor.get_flag_rule("to_zip")
    file_path_monitor = zimatise_monitor.get_file_path_monitor()

    while True:
        list_project_path = utils.get_list_project_to_process(
            file_path_monitor, flag_rule
        )
        utils.clean_cmd()
        show_projects_to_zip(list_project_path)
        project_path = utils.select_a_project_to_process(list_project_path)
        if project_path == "":
            time.sleep(5)
            continue
        success = process_zipind(project_path)
        if success:
            # set stage 2_auto_zip
            zimatise_monitor.set_stage_project(
                project_path, stage_name="2_auto_zip", stage_value=1
            )
        else:
            pass

        time.sleep(5)


if __name__ == "__main__":
    logging_config()
    main()
