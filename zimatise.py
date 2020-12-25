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

try:
    import mass_videojoin
    from timestamp_link_maker import timestamp_link_maker
    import telegram_filesender
    import zipind

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
    import telegram_filesender
    import zipind


def logging_config():

    logfilename = 'log-' + 'zimatise' + '.txt'
    logging.basicConfig(filename=logfilename, level=logging.DEBUG,
                        format=' %(asctime)s-%(levelname)s-%(message)s')
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(' %(asctime)s-%(levelname)s-%(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def ensure_folder_existence(folders_path):
    """
    :input: folders_path: List
    """

    for folder_path in folders_path:
        existence = os.path.isdir(folder_path)
        if existence is False:
            os.mkdir(folder_path)


def get_path_folder_output():

    path_folder_origin = get_name_dir_origin()
    path_folder_output = 'output_' + path_folder_origin
    ensure_folder_existence([path_folder_output])
    return path_folder_output


def get_txt_content(file_path):

    file = open(file_path, 'r', encoding='utf-8')
    file_content = file.readlines()
    file_content = ''.join(file_content)
    file.close()
    return file_content


def get_txt_folder_origin():

    file_folder_name = 'folder_files_origin.txt'
    if os.path.exists(file_folder_name) is False:
        open(file_folder_name, 'a').close()
    return file_folder_name


def get_name_dir_origin():

    name_file_folder_name = get_txt_folder_origin()
    dir_name_saved = get_txt_content(name_file_folder_name)
    return dir_name_saved


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
        raise MyValidationError(msg_invalid_option)


def get_how_many_files_in_folder(path_folder):

    count = len([name for name in os.listdir(path_folder)
                 if os.path.join(path_folder, name)])
    return count


def get_start_index_output():

    path_folder_output_files = os.path.join(get_path_folder_output(),
                                            'output_videos')
    count_files = get_how_many_files_in_folder(path_folder_output_files)
    start_index_output = count_files + 1
    return start_index_output


def play_sound():

    path_file_sound = ''
    os.system(f'start wmplayer "{path_file_sound}"')


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
    folder_files_origin = get_txt_folder_origin()

    # get path_file of video_details.xlsx
    path_file_report = mass_videojoin.set_path_file_report()

    menu_answer = menu_ask()
    if menu_answer == 1:
        # Zip not video files
        path_dir = input('\nPaste the folder link where are the video files: ')
        mass_videojoin.save_upload_folder_name(path_dir, folder_files_origin)

        mb_limit = int(mass_videojoin.userpref_size_per_file_mb())

        path_folder_output = os.path.join(get_path_folder_output(),
                                          'output_videos')
        ensure_folder_existence([path_folder_output])
        zipind.zipind(path_dir=path_dir, mb_per_file=mb_limit,
                      path_dir_output=path_folder_output)
        # break_point
        input('Zip files created.')

        mass_videojoin.clean_cmd()
        main()
        return

    elif menu_answer == 2:
        # create Dataframe of video details
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

    elif menu_answer == 3:
        # reencode videos mark in column video_resolution_to_change
        mass_videojoin.set_make_reencode(path_file_report)

        # play_sound()

        # break_point
        input('Review the file and then type something to continue.')
        mass_videojoin.clean_cmd()

        main()
        return

    elif menu_answer == 4:
        # join videos
        mb_limit = int(mass_videojoin.userpref_size_per_file_mb())

        # establishes separation criteria for the join videos step
        mass_videojoin.set_group_column(path_file_report)

        # break_point
        input('Review the file and then type something to ' +
              'start the process that look for videos that ' +
              'are too big and should be splitted')

        # split videos too big
        mass_videojoin.set_split_videos(path_file_report, mb_limit)

        # start_index_output
        # start_index_output = get_start_index_output()

        # start_index_number = input('(None for 1) Answer: ')

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
        start_index_number = get_start_index_number()

        # join all videos
        mass_videojoin.set_join_videos(path_file_report, mb_limit,
                                       start_index_output=start_index_number)

        # play_sound()
        # break_point
        input('')
        mass_videojoin.clean_cmd()

        main()
        return

    elif menu_answer == 5:
        # timestamp maker
        path_folder_output = get_path_folder_output()

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
        input('TimeStamp and descriptions files created')
        mass_videojoin.clean_cmd()
        main()
        return

    elif menu_answer == 6:
        # file sender
        path_folder_output = get_path_folder_output()
        telegram_filesender.main(folder_path_descriptions=path_folder_output)

        # break_point
        input('All files were sent to the telegram')
        mass_videojoin.clean_cmd()
        return


if __name__ == "__main__":
    logging_config()
    main()
