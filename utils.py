import os


def ensure_folder_existence(folders_path):
    """
    :input: folders_path: List
    """

    for folder_path in folders_path:
        existence = os.path.isdir(folder_path)
        if existence is False:
            os.mkdir(folder_path)


def get_txt_content(file_path):

    file = open(file_path, 'r', encoding='utf-8')
    file_content = file.readlines()
    file_content = ''.join(file_content)
    file.close()
    return file_content


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


def get_txt_folder_origin():

    file_folder_name = 'folder_files_origin.txt'
    if os.path.exists(file_folder_name) is False:
        open(file_folder_name, 'a').close()
    return file_folder_name


def get_path_folder_output():

    def get_name_dir_origin():

        name_file_folder_name = get_txt_folder_origin()
        dir_name_saved = get_txt_content(name_file_folder_name)
        return dir_name_saved

    path_folder_origin = get_name_dir_origin()
    path_folder_output = 'output_' + path_folder_origin
    ensure_folder_existence([path_folder_output])
    return path_folder_output
