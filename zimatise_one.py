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
    -https://github.com/apenasrr/mass_videojoin
    -https://github.com/apenasrr/timestamp_link_maker
    -https://github.com/apenasrr/telegram_filesender

    ## How to use
    -Place the folder of the 4 required repositories and this repository in the
    same location. Then there must be 5 folders in the same location
    -Enter the 'zimatise' folder and run the zimatise.py file
    -Follow the on-screen instructions
    -For more details, check the documentation for the required repositories

    Do you wish to buy a coffee to say thanks?
    LBC (from LBRY) digital Wallet
    > bFmGgebff4kRfo5pXUTZrhAL3zW2GXwJSX

    We recommend:
    mises.org - Educate yourself about economic and political freedom
    lbry.tv - Store files and videos on blockchain ensuring free speech
    https://www.activism.net/cypherpunk/manifesto.html -  How encryption is essential to Free Speech and Privacy
"""

import logging
import os

import update_description_summary
import utils
from header_maker import header_maker

try:
    import config_data
    import mass_videojoin
    import telegram_filesender
    import zipind
    import zipind_core
    from timestamp_link_maker import timestamp_link_maker

except:

    list_folders_name = [
        "Zipind",
        "mass_videojoin",
        "timestamp_link_maker",
        "Telegram_filesender",
    ]
    utils.add_path_script_folders(list_folders_name)
    import config_data
    import mass_videojoin
    import telegram_filesender
    import zipind
    import zipind_core
    from timestamp_link_maker import timestamp_link_maker


def logging_config():

    logfilename = "log-" + "zimatise" + ".txt"
    logging.basicConfig(
        level=logging.INFO,
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


def menu_ask():

    # fmt: off
    print("1-Create independent Zip parts for not_video_files")
    print("2-Generate worksheet listing the files")
    print("3-Process reencode of videos marked in column "
          '"video_resolution_to_change"')
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

    path_file_sound = ""
    os.system(f'start wmplayer "{path_file_sound}"')


def define_mb_per_file(path_file_config, file_size_limit_mb):

    if file_size_limit_mb is not None:
        repeat_size = input(
            f"Define limit of {file_size_limit_mb} " + "MB per file? y/n\n"
        )
        if repeat_size == "n":
            file_size_limit_mb = zipind.ask_mb_file()
            zipind.config_update_data(
                path_file_config, "file_size_limit_mb", str(file_size_limit_mb)
            )
    else:
        file_size_limit_mb = zipind.ask_mb_file()
        zipind.config_update_data(
            path_file_config, "file_size_limit_mb", str(file_size_limit_mb)
        )
    return file_size_limit_mb


def main():
    """
    How to use
    -Place the folder of the 4 required repositories and this repository in
    the same location. Then there must be 5 folders in the same location
    -Enter the 'zimatise' folder and run the zimatise.py file
    -Follow the on-screen instructions
    -For more details, check the documentation for the required repositories
    Source: https://github.com/apenasrr/zimatise
    """

    # get config data
    folder_script_path = utils.get_folder_script_path()
    path_file_config = os.path.join(folder_script_path, "config.ini")
    config = utils.get_config_data(path_file_config)
    file_size_limit_mb = int(config["file_size_limit_mb"])
    mode = config["mode"]
    max_path = int(config["max_path"])
    list_video_extensions = config["video_extensions"].split(",")
    duration_limit = config["duration_limit"]
    activate_transition = config["activate_transition"]
    start_index = int(config["start_index"])
    hashtag_index = config["hashtag_index"]
    path_summary_top = config["path_summary_top"]
    path_summary_bot = config["path_summary_bot"]
    document_hashtag = config["document_hashtag"]
    document_title = config["document_title"]

    dict_summary = {}
    dict_summary["path_summary_top"] = path_summary_top
    dict_summary["path_summary_bot"] = path_summary_bot

    file_path_report = None
    folder_path_report = None
    utils.ensure_folder_existence(["projects"])
    while True:
        menu_answer = menu_ask()

        # 1-Create independent Zip parts for not_video_files
        if menu_answer == 1:
            # Zip not video files

            # fmt: off
            folder_path_report = \
                mass_videojoin.get_path_dir(folder_path_report)
            file_path_report = \
                mass_videojoin.set_path_file_report(folder_path_report)
            folder_path_project = os.path.dirname(file_path_report)

            if os.path.isdir(folder_path_report) is False:
                input("\nThe folder does not exist.")
                mass_videojoin.clean_cmd()
                continue

            file_size_limit_mb = define_mb_per_file(
                path_file_config, file_size_limit_mb
            )

            # fmt: off
            if zipind.ensure_folder_sanitize(folder_path_report,
                                             max_path) is False:
                mass_videojoin.clean_cmd()
                continue

            folder_path_output = os.path.join(folder_path_project,
                                              "output_videos")
            utils.ensure_folder_existence([folder_path_output])
            zipind_core.zipind(
                path_dir=folder_path_report,
                mb_per_file=file_size_limit_mb,
                path_dir_output=folder_path_output,
                mode=mode,
                ignore_extensions=list_video_extensions,
            )
            # break_point
            input("\nZip files created.")

            mass_videojoin.clean_cmd()
            continue

        # 2-Generate worksheet listing the files
        # create Dataframe of video details
        elif menu_answer == 2:

            # fmt: off
            folder_path_report = \
                mass_videojoin.get_path_dir(folder_path_report)
            file_path_report = \
                mass_videojoin.set_path_file_report(folder_path_report)

            mass_videojoin.step_create_report_filled(
                folder_path_report, file_path_report, list_video_extensions
            )

            # fmt: off
            print("\nIf necessary, change the reencode plan in the column "
                  '"video_resolution_to_change"')

            # break_point
            input("Type Enter to continue")

            mass_videojoin.clean_cmd()
            continue

        # 3-reencode videos and recheck duration
        #       -reencode videos mark in column video_resolution_to_change
        #       -recheck to correct duration metadata
        elif menu_answer == 3:

            # define variables
            # fmt: off
            folder_path_report = \
                mass_videojoin.get_path_dir(folder_path_report)

            file_path_report = \
                mass_videojoin.set_path_file_report(folder_path_report)

            folder_path_videos_encoded = \
                mass_videojoin.set_path_folder_videos_encoded(folder_path_report)
            mass_videojoin.ensure_folder_existence([folder_path_videos_encoded])

            # reencode videos mark in column video_resolution_to_change
            mass_videojoin.set_make_reencode(file_path_report,
                                             folder_path_videos_encoded)

            # play_sound()

            # correct videos duration
            print("start correcting the duration metadata")
            mass_videojoin.set_correct_duration(file_path_report)

            # break_point
            input(
                "Duration metadata corrected.\n"
                + "Type something to go to the main menu, "
                + 'and proceed to the "Group videos" process.'
            )

            mass_videojoin.clean_cmd()
            continue

        # 4-join videos
        #       -Group videos with the same codec and resolution')
        elif menu_answer == 4:

            # define variables
            # fmt: off
            folder_path_report = \
                mass_videojoin.get_path_dir(folder_path_report)
            # fmt: off
            file_path_report = \
                mass_videojoin.set_path_file_report(folder_path_report)
            # fmt: off
            folder_path_videos_splitted = \
                mass_videojoin.set_path_folder_videos_splitted(folder_path_report)

            # fmt: off
            mass_videojoin.ensure_folder_existence([folder_path_videos_splitted])
            # fmt: off
            folder_path_videos_joined = \
                mass_videojoin.set_path_folder_videos_joined(folder_path_report)

            mass_videojoin.ensure_folder_existence([folder_path_videos_joined])

            filename_output = mass_videojoin.get_folder_name_normalized(
                folder_path_report
            )

            # fmt: off
            folder_path_videos_cache = \
                mass_videojoin.set_path_folder_videos_cache(folder_path_report)

            mass_videojoin.ensure_folder_existence([folder_path_videos_cache])

            # Fill group_column.
            #  Establishes separation criteria for the join videos step
            mass_videojoin.set_group_column(file_path_report)

            # break_point
            # fmt: off
            input("Review the file and then type something to "
                  "start the process that look for videos that "
                  "are too big and should be splitted")

            # split videos too big
            mass_videojoin.set_split_videos(
                file_path_report,
                file_size_limit_mb,
                folder_path_videos_splitted,
                duration_limit,
            )

            # join all videos
            mass_videojoin.set_join_videos(
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
            # fmt: off
            input('\nAll videos were grouped. '
                  'Go to the "Make Time Stamps" step.')

            mass_videojoin.clean_cmd()
            continue

        # '5-Make Descriptions report with timestamps, summary.txt
        #     and head_project.txt'
        elif menu_answer == 5:
            # timestamp maker

            # define variables

            # fmt: off
            folder_path_report = \
                mass_videojoin.get_path_dir(folder_path_report)

            # fmt: off
            file_path_report = \
                mass_videojoin.set_path_file_report(folder_path_report)

            folder_path_project = os.path.dirname(file_path_report)

            # make descriptions.xlsx and summary.txt
            timestamp_link_maker(
                folder_path_output=folder_path_project,
                file_path_report_origin=file_path_report,
                hashtag_index=hashtag_index,
                start_index_number=start_index,
                dict_summary=dict_summary,
            )

            # fmt: off
            update_description_summary.main(
                path_summary_top,
                folder_path_project,
                document_hashtag,
                document_title
            )

            # make header project
            header_maker(folder_path_project)
            print("\nTimeStamp and descriptions files created.")

            # break point
            input("\nType something to go to the main menu")

            mass_videojoin.clean_cmd()
            continue

        # '6-Auto-send to Telegram'
        elif menu_answer == 6:
            # file sender

            # define variables
            # fmt: off
            folder_path_report = \
                mass_videojoin.get_path_dir(folder_path_report)

            # fmt: off
            file_path_report = \
                mass_videojoin.set_path_file_report(folder_path_report)

            # fmt: off
            folder_path_project = \
                os.path.dirname(file_path_report)

            # Generate config_data dictionary from config_data
            #  in repo telegram_filesender
            dict_config = config_data.config_data()
            print(f"\nProject: {folder_path_project}\n")

            telegram_filesender.main(folder_path_project, dict_config)

            # break_point
            input("All files were sent to the telegram")
            mass_videojoin.clean_cmd()
            return


if __name__ == "__main__":
    logging_config()
    main()
