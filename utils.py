import os
from configparser import ConfigParser


def get_config_data(path_file_config):
    """get default configuration data from file config.ini

    Returns:
        dict: config data
    """

    config_file = ConfigParser()
    config_file.read(path_file_config)
    default_config = dict(config_file['default'])
    return default_config


def ensure_folder_existence(folders_path):
    """
    :input: folders_path: List
    """

    for folder_path in folders_path:
        existence = os.path.isdir(folder_path)
        if existence is False:
            os.mkdir(folder_path)


def get_txt_content(file_path):

    list_encode = ['utf-8', 'ISO-8859-1']  # utf8, ansi
    for encode in list_encode:
        try:
            file = open(file_path, 'r', encoding=encode)
            file_content = file.readlines()
            file_content = ''.join(file_content)
            file.close()
            return file_content
        except:
            continue

    file = open(file_path, 'r', encoding=encode)
    file_content = file.readlines()
    raise Exception('encode', f'Cannot open file: {file_path}')


def create_txt(file_path, stringa):

    f = open(file_path, "w", encoding='utf8')
    f.write(stringa)
    f.close()


def format_time_delta(time_delta):

    days = time_delta.days
    totalSeconds = time_delta.seconds
    hours, remainder = divmod(totalSeconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    hours = days*24 + hours
    return f'{hours}h {minutes}min'


def compile_template(d_keys, template_content):

    for key in d_keys.keys():
        template_content = \
            template_content.replace('{' + key + '}', d_keys[key])
    output_content = template_content
    return output_content
