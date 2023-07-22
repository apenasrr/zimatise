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

    ## How to use
    - Update the libs through the 'update_libs.bat' file
    - Run the zimatise_one.py file
    - Follow the on-screen instructions
    - For more details, check the repository

    Do you wish to buy a coffee to say thanks?
    LBC (from LBRY) digital Wallet
    > bFmGgebff4kRfo5pXUTZrhAL3zW2GXwJSX

    We recommend:
    mises.org - Educate yourself about economic and political freedom
    lbry.tv - Store files and videos on blockchain ensuring free speech
    https://www.activism.net/cypherpunk/manifesto.html -  How encryption is essential to Free Speech and Privacy
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import vidtool
import zipind
from tgsender import tgsender

import autopost_summary
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


def run_silent_mode(
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
    config_data,
):
    folder_path_project = vidtool.get_folder_path(folder_path_project)
    file_path_report = vidtool.set_path_file_report(folder_path_project)
    folder_path_report = file_path_report.parent
    folder_path_output = folder_path_report / "output_videos"

    ################################### p1
    utils.ensure_folder_existence([folder_path_output])
    zipind.zipind_core.run(
        path_folder=folder_path_project,
        mb_per_file=file_size_limit_mb,
        path_folder_output=folder_path_output,
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
    vidtool.ensure_folder_existence([folder_path_videos_encoded])

    # reencode videos mark in column video_resolution_to_change
    vidtool.set_make_reencode(file_path_report, folder_path_videos_encoded)

    ################################### p4

    folder_path_videos_splitted = vidtool.set_path_folder_videos_splitted(
        folder_path_project
    )

    vidtool.ensure_folder_existence([folder_path_videos_splitted])

    folder_path_videos_joined = vidtool.set_path_folder_videos_joined(
        folder_path_project
    )

    vidtool.ensure_folder_existence([folder_path_videos_joined])

    filename_output = vidtool.get_folder_name_normalized(folder_path_project)

    folder_path_videos_cache = vidtool.set_path_folder_videos_cache(
        folder_path_project
    )

    vidtool.ensure_folder_existence([folder_path_videos_cache])

    if reencode_plan == "group":
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

    if reencode_plan == "group":
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

    # TODO: tgsender config
    print(f"\nProject: {folder_path_report}\n")

    # TODO: call tgsender.main

    tgsender.send_via_telegram_api(Path(folder_path_report), config_data)

    # Post and Pin summary
    autopost_summary.run(folder_path_report)

    # Register invite_link
    if register_invite_link == "1":
        project_metadata.include(folder_path_project, folder_path_report)

    utils.move_project(folder_path_project, config_data)


def main():
    """
    -For instructions, check the documentation in
    https://github.com/apenasrr/zimatise
    """

    # get config data
    folder_script_path = utils.get_folder_script_path()
    file_path_config = folder_script_path / "config.ini"
    config_data = utils.get_config_data(file_path_config)
    file_size_limit_mb = int(config_data["file_size_limit_mb"])
    mode = config_data["mode"]
    max_path = int(config_data["max_path"])
    list_video_extensions = config_data["video_extensions"].split(",")
    duration_limit = config_data["duration_limit"]
    activate_transition = config_data["activate_transition"]
    start_index = int(config_data["start_index"])
    hashtag_index = config_data["hashtag_index"]
    reencode_plan = config_data["reencode_plan"]

    descriptions_auto_adapt_str = config_data["descriptions_auto_adapt"]
    if descriptions_auto_adapt_str == "true":
        descriptions_auto_adapt = True
    else:
        descriptions_auto_adapt = False

    silent_mode_str = config_data["silent_mode"]
    if silent_mode_str == "true":
        silent_mode = True
    else:
        silent_mode = False

    path_summary_top = Path("user") / config_data["path_summary_top"]
    path_summary_bot = Path("user") / config_data["path_summary_bot"]
    document_hashtag = config_data["document_hashtag"]
    document_title = config_data["document_title"]
    register_invite_link = config_data["register_invite_link"]

    dict_summary = {}
    dict_summary["path_summary_top"] = path_summary_top
    dict_summary["path_summary_bot"] = path_summary_bot
    file_path_report = None
    folder_path_project = None
    utils.ensure_folder_existence([Path("projects")])

    if silent_mode:
        while True:
            ensure_silent_mode = input("Continue to silent mode? (y/n) ")
            if ensure_silent_mode != "y" and ensure_silent_mode != "":
                break
            run_silent_mode(
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
                config_data,
            )
            input("\nProject processed and sent to Telegram")
            vidtool.clean_cmd()

    while True:
        menu_answer = menu_ask()

        # 1-Create independent Zip parts for not_video_files
        if menu_answer == 1:
            # Zip not video files

            folder_path_project = vidtool.get_folder_path(folder_path_project)
            file_path_report = vidtool.set_path_file_report(
                folder_path_project
            )
            folder_path_report = file_path_report.parent

            if not folder_path_project.exists():
                input("\nThe folder does not exist.")
                vidtool.clean_cmd()
                continue

            file_size_limit_mb = define_mb_per_file(
                file_path_config, file_size_limit_mb
            )

            if (
                zipind.zipind.ensure_folder_sanitize(
                    folder_path_project, max_path
                )
                is False
            ):
                vidtool.clean_cmd()
                continue

            folder_path_output = folder_path_report / "output_videos"
            utils.ensure_folder_existence([folder_path_output])
            zipind.zipind_core.run(
                path_folder=folder_path_project,
                mb_per_file=file_size_limit_mb,
                path_folder_output=folder_path_output,
                mode=mode,
                ignore_extensions=list_video_extensions,
            )

            # break_point
            input("\nZip files created.")

            vidtool.clean_cmd()
            continue

        # 2-Generate worksheet listing the files
        # create Dataframe of video details
        elif menu_answer == 2:
            folder_path_project = vidtool.get_folder_path(folder_path_project)
            file_path_report = vidtool.set_path_file_report(
                folder_path_project
            )

            vidtool.step_create_report_filled(
                folder_path_project,
                file_path_report,
                list_video_extensions,
                reencode_plan,
            )

            print(
                "\nIf necessary, change the reencode plan in the column "
                '"video_resolution_to_change"'
            )

            # break_point
            input("Type Enter to continue")

            vidtool.clean_cmd()
            continue

        # 3-reencode videos and recheck duration
        #       -reencode videos mark in column video_resolution_to_change
        #       -recheck to correct duration metadata
        elif menu_answer == 3:
            # define variables
            folder_path_project = vidtool.get_folder_path(folder_path_project)

            file_path_report = vidtool.set_path_file_report(
                folder_path_project
            )

            folder_path_videos_encoded = (
                vidtool.set_path_folder_videos_encoded(folder_path_project)
            )
            vidtool.ensure_folder_existence([folder_path_videos_encoded])

            # reencode videos mark in column video_resolution_to_change
            vidtool.set_make_reencode(
                file_path_report, folder_path_videos_encoded
            )

            # play_sound()

            # correct videos duration
            if reencode_plan == "group":
                print("start correcting the duration metadata")
                vidtool.set_correct_duration(file_path_report)

                # break_point
                print("Duration metadata corrected.")
            input(
                "Type something to go to the main menu, "
                + 'and proceed to the "Group videos" process.'
            )
            vidtool.clean_cmd()
            continue

        # 4-join videos
        #       -Group videos with the same codec and resolution')
        elif menu_answer == 4:
            # define variables

            folder_path_project = vidtool.get_folder_path(folder_path_project)

            file_path_report = vidtool.set_path_file_report(
                folder_path_project
            )

            folder_path_videos_splitted = (
                vidtool.set_path_folder_videos_splitted(folder_path_project)
            )

            vidtool.ensure_folder_existence([folder_path_videos_splitted])

            folder_path_videos_joined = vidtool.set_path_folder_videos_joined(
                folder_path_project
            )

            vidtool.ensure_folder_existence([folder_path_videos_joined])

            filename_output = vidtool.get_folder_name_normalized(
                folder_path_project
            )

            folder_path_videos_cache = vidtool.set_path_folder_videos_cache(
                folder_path_project
            )

            vidtool.ensure_folder_existence([folder_path_videos_cache])

            if not vidtool.join_process_has_started(file_path_report):
                if reencode_plan == "group":
                    # Fill group_column.
                    #  Establishes separation criteria for the join videos step
                    vidtool.set_group_column(file_path_report)

                    # break_point

                    input(
                        "Review the file and then type something to "
                        "start the process that look for videos that "
                        "are too big and should be splitted"
                    )

                # split videos too big
                vidtool.set_split_videos(
                    file_path_report,
                    file_size_limit_mb,
                    folder_path_videos_splitted,
                    duration_limit,
                )

            if reencode_plan == "group":
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

                # play_sound()

                # break_point

                print("\nAll videos were grouped")
            else:
                pass
            input('Go to the "Make Time Stamps" step.')
            vidtool.clean_cmd()
            continue

        # '5-Make Descriptions report with timestamps, summary.txt
        #     and head_project.txt'
        elif menu_answer == 5:
            # timestamp maker

            # define variables

            folder_path_project = vidtool.get_folder_path(folder_path_project)

            file_path_report = vidtool.set_path_file_report(
                folder_path_project
            )

            folder_path_report = file_path_report.parent

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
            print("\nTimeStamp and descriptions files created.")

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
                # break point
                input("\nType something to go to the main menu")
            vidtool.clean_cmd()
            continue

        # '6-Auto-send to Telegram'
        elif menu_answer == 6:
            # file sender

            # define variables

            folder_path_project = vidtool.get_folder_path(folder_path_project)

            file_path_report = vidtool.set_path_file_report(
                folder_path_project
            )

            folder_path_report = file_path_report.parent

            # Generate config_data dictionary from config_data
            #  in repo tgsender
            print(f"\nProject: {folder_path_report}\n")

            # TODO: Enable sending files in macro keyboard mode
            # Send project

            tgsender.send_via_telegram_api(
                Path(folder_path_report), config_data
            )

            # Post and Pin summary
            autopost_summary.run(folder_path_report)

            # Register invite_link
            if register_invite_link == "1":
                project_metadata.include(
                    folder_path_project, folder_path_report
                )

            input("All files were sent to the telegram")
            vidtool.clean_cmd()

            utils.move_project(folder_path_project, config_data)
            return


if __name__ == "__main__":
    logging_config()
    main()
