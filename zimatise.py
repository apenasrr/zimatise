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
import sys
import utils
from header_maker import header_maker

try:
    import mass_videojoin
    from timestamp_link_maker import timestamp_link_maker
    import telegram_filesender, config_data
    import zipind, zipind_core

except:
    def add_path_script_folders(list_folders_name):

        list_repo_dont_found = []
        for folder_name in list_folders_name:
            path_script_folder = os.path.abspath(
                os.path.join('..', folder_name))
            existence = os.path.isdir(path_script_folder)
            if existence is False:
                list_repo_dont_found.append(path_script_folder)
            else:
                sys.path.append(path_script_folder)

        # alert in case of not found repositories
        qt_not_found = len(list_repo_dont_found)
        if qt_not_found != 0:
            if qt_not_found > 1:
                repo = 'repositories'
            else:
                repo = 'repository'
            str_list_repo_dont_found = '\n'.join(list_repo_dont_found)
            logging.error(f'The {repo} below could not be found. ' +
                          'Make sure it exists with the proper folder ' +
                          f'name.\n{str_list_repo_dont_found}\n')
            exit()

    list_folders_name = ['Zipind', 'mass_videojoin', 'timestamp_link_maker',
                         'Telegram_filesender']
    add_path_script_folders(list_folders_name)
    import mass_videojoin
    from timestamp_link_maker import timestamp_link_maker
    import telegram_filesender, config_data
    import zipind, zipind_core


def logging_config():

    logfilename = 'log-' + 'zimatise' + '.txt'
    logging.basicConfig(
        level=logging.DEBUG,
        format=' %(asctime)s-%(levelname)s-%(message)s',
        handlers=[logging.FileHandler(logfilename, 'w', 'utf-8')])
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(' %(asctime)s-%(levelname)s-%(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def menu_ask():

    print('1-Create independent Zip parts for not_video_files')
    print('2-Generate worksheet listing the files')
    print('3-Process reencode of videos marked in column ' +
          '"video_resolution_to_change"')
    print('4-Group videos with the same codec and resolution')
    print('5-Make Timestamps and Descriptions report')
    print('6-Auto-send to Telegram')

    msg_type_answer = 'Type your answer: '
    make_report = int(input(f'\n{msg_type_answer}'))
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


def get_how_many_files_in_folder(path_folder):

    count = len([name for name in os.listdir(path_folder)
                 if os.path.join(path_folder, name)])
    return count


def get_start_index_output():

    path_folder_output_files = os.path.join(utils.get_path_folder_output(),
                                            'output_videos')
    count_files = get_how_many_files_in_folder(path_folder_output_files)
    start_index_output = count_files + 1
    return start_index_output


def play_sound():

    path_file_sound = ''
    os.system(f'start wmplayer "{path_file_sound}"')


def get_start_index_number():

    while True:
        print('Start hashtag index count with what value?')
        start_index_number = input('(None for 1) Answer: ')
        if start_index_number == '':
            start_index_number = 1
            return start_index_number
        else:
            if start_index_number.isdigit():
                start_index_number = int(start_index_number)
                return start_index_number
            else:
                pass


def get_folder_script_path():

    folder_script_path_relative = os.path.dirname(__file__)
    folder_script_path = os.path.realpath(folder_script_path_relative)

    return folder_script_path


def define_mb_per_file(path_file_config, file_size_limit_mb):

    if file_size_limit_mb is not None:
        repeat_size = input(f'Define limit of {file_size_limit_mb} ' +
                            'MB per file? y/n\n')
        if repeat_size == 'n':
            file_size_limit_mb = zipind.ask_mb_file()
            zipind.config_update_data(path_file_config, 'file_size_limit_mb',
                                      str(file_size_limit_mb))
    else:
        file_size_limit_mb = zipind.ask_mb_file()
        zipind.config_update_data(path_file_config, 'file_size_limit_mb',
                                  str(file_size_limit_mb))
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

    mass_videojoin.ensure_folders_existence()
    folder_files_origin = utils.get_txt_folder_origin()

    # get path_file of video_details.xlsx
    path_file_report = mass_videojoin.set_path_file_report()

    folder_script_path = get_folder_script_path()
    path_file_config = os.path.join(folder_script_path, 'config.ini')
    config = utils.get_config_data(path_file_config)
    file_size_limit_mb = int(config['file_size_limit_mb'])
    mode = config['mode']
    max_path = int(config['max_path'])
    list_video_extensions = config['video_extensions'].split(',')

    menu_answer = menu_ask()

    # 1-Create independent Zip parts for not_video_files
    if menu_answer == 1:
        # Zip not video files
        path_dir = input('\nPaste the folder link where are the video files: ')
        if os.path.isdir(path_dir) is False:
            input('\nThe folder does not exist.')
            mass_videojoin.clean_cmd()
            main()
            return
        mass_videojoin.save_upload_folder_name(path_dir, folder_files_origin)

        file_size_limit_mb = define_mb_per_file(path_file_config,
                                                file_size_limit_mb)

        if zipind.ensure_folder_sanatize(path_dir, max_path) is False:
            mass_videojoin.clean_cmd()
            main()
            return

        path_folder_output = os.path.join(utils.get_path_folder_output(),
                                          'output_videos')
        utils.ensure_folder_existence([path_folder_output])
        zipind_core.zipind(path_dir=path_dir, mb_per_file=file_size_limit_mb,
                           path_dir_output=path_folder_output,
                           mode=mode,
                           ignore_extensions=list_video_extensions)
        # break_point
        input('Zip files created.')

        mass_videojoin.clean_cmd()
        main()
        return

    # 2-Generate worksheet listing the files
    # create Dataframe of video details
    elif menu_answer == 2:
        path_dir = input('\nPaste the folder link where are the video files: ')
        # save in txt, the folder name
        mass_videojoin.save_upload_folder_name(path_dir, folder_files_origin)

        path_file_report = mass_videojoin.set_path_file_report()

        mass_videojoin.step_create_report_filled(path_dir, path_file_report)

        print('\nIf necessary, change the reencode plan in the column ' +
              '"video_resolution_to_change"')
        # break_point
        input('Type Enter to continue')
        mass_videojoin.clean_cmd()
        main()
        return

    # '3-Process reencode of videos marked in column ' +
    #  '"video_resolution_to_change"')
    # reencode videos mark in column video_resolution_to_change
    elif menu_answer == 3:
        mass_videojoin.set_make_reencode(path_file_report)

        # play_sound()

        # break_point
        # input('type something to start correcting the duration metadata...')
        mass_videojoin.set_correct_duration(path_file_report)

        # break_point
        input('Duration metadata corrected.\n' +
              'Type something to go to the main menu, ' +
              'and proceed to the "Group videos" process.')
        mass_videojoin.clean_cmd()

        main()
        return

    # '4-Group videos with the same codec and resolution')
    # join videos
    elif menu_answer == 4:

        # ask start_index_number to user
        start_index_number = get_start_index_number()

        mb_limit = int(mass_videojoin.userpref_size_per_file_mb())

        duration_limit = mass_videojoin.get_duration_limit()

        # establishes separation criteria for the join videos step
        mass_videojoin.set_group_column(path_file_report)

        # break_point
        input('Review the file and then type something to ' +
              'start the process that look for videos that ' +
              'are too big and should be splitted')

        # split videos too big
        mass_videojoin.set_split_videos(path_file_report, mb_limit,
                                        duration_limit)


        # join all videos
        mass_videojoin.set_join_videos(path_file_report, mb_limit,
                                       duration_limit,
                                       start_index_output=start_index_number)

        # play_sound()
        # break_point
        input('')
        mass_videojoin.clean_cmd()

        main()
        return

    # '5-Make Timestamps and Descriptions report')
    elif menu_answer == 5:
        # timestamp maker
        path_folder_output = utils.get_path_folder_output()

        print('Start hashtag index count with what value?')
        start_index_number = input('(None for 1) Answer: ')
        if start_index_number == '':
            start_index_number = 1
        else:
            start_index_number = int(start_index_number)

        timestamp_link_maker(folder_path_output=path_folder_output,
                             file_path_report_origin=path_file_report,
                             start_index_number=start_index_number)
        # break_point
        input('\nTimeStamp and descriptions files created')

        header_maker()
        input('\nType something to go to the main menu')
        mass_videojoin.clean_cmd()
        main()
        return

    # '6-Auto-send to Telegram')
    elif menu_answer == 6:
        # file sender
        path_folder_output = utils.get_path_folder_output()
        #  Generate config_data dictionary
        dict_config = config_data.config_data()
        print(f'\nProject: {path_folder_output}\n')

        telegram_filesender.main(folder_path_descriptions=path_folder_output,
                                 dict_config=dict_config)

        # break_point
        input('All files were sent to the telegram')
        mass_videojoin.clean_cmd()
        return


if __name__ == "__main__":
    logging_config()
    main()
