import json
from pathlib import Path


def get_dict_metadata(folder_path_report):

    channel_metadata_path = Path(folder_path_report) / "channel_metadata"
    if not channel_metadata_path.exists():
        return None
    with open(channel_metadata_path, encoding="utf-8") as f:
        list_content = f.readlines()
        str_content = "".join(list_content)
        dict_metadata = eval(str_content)
        f.close()
    return dict_metadata


def update_project_config(project_config_path, dict_data):

    if project_config_path.exists():
        # update .config file
        with open(project_config_path, "r", encoding="utf-8") as f:
            project_metadata = json.load(f)
            project_metadata.update(dict_data)
    else:
        project_metadata = dict_data

    with open(project_config_path, "w", encoding="utf-8") as f:
        json.dump(project_metadata, f)


def include(folder_path_project, folder_path_report):

    dict_metadata = get_dict_metadata(folder_path_report)
    if not dict_metadata:
        return False
    chat_invite_link = dict_metadata.get("chat_invite_link", "")
    if chat_invite_link == "":
        return False
    else:
        dict_data = {"stream_link": chat_invite_link}
    project_config_path = Path(folder_path_project) / ".config"
    update_project_config(project_config_path, dict_data)
