import logging
import os

import tgsender

from utils import compile_template, get_txt_content


def send_header(moc_chat_id: int, header_content: str):

    tgsender.api.send_message(chat_id=moc_chat_id, text=header_content)


def get_chat_invite_link(folder_path_project: str):

    file_path_metadata = os.path.join(folder_path_project, "channel_metadata")
    if os.path.exists(file_path_metadata):

        dict_metadata = eval(get_txt_content(file_path_metadata))
        chat_invite_link = dict_metadata["chat_invite_link"]
        return chat_invite_link
    else:
        raise Exception(
            "No metadata file found. Make sure the channel was created"
        )


def get_header_content(folder_path_project: str):
    """captures the content of the project header

    Args:
        folder_path_project (str): Project Analysis Folder Path
    """

    file_path_header = os.path.join(folder_path_project, "header_project.txt")
    header_content = get_txt_content(file_path_header)
    return header_content


def get_template_moc(file_path_template_moc):

    template_moc = get_txt_content(file_path_template_moc)

    return template_moc


def showcase_formater(template_moc: str, content: str, chat_invite_link: str):

    d_keys = {"header_chat": content}
    header_content_raw1 = compile_template(
        d_keys, template_content=template_moc
    )

    header_content_raw2 = "\n".join(header_content_raw1.split("\n")[2:])

    d_keys = {"chat_invite_link": chat_invite_link}
    header_content = compile_template(
        d_keys, template_content=header_content_raw2
    )
    return header_content


def pipe_publish(
    moc_chat_id: int, file_path_template_moc: str, folder_path_project: str
):
    """Publishes the project info on the map of content (MOC) chat

    Args:
        moc_chat_id (int): chat id of MOC
        file_path_template_moc (str): MOC template file path
        folder_path_project (str): Project Analysis Folder Path
    """

    chat_invite_link = get_chat_invite_link(folder_path_project)
    header_content = get_header_content(folder_path_project)
    template_moc = get_txt_content(file_path_template_moc)
    showcase_content = showcase_formater(
        template_moc, header_content, chat_invite_link
    )

    send_header(moc_chat_id, showcase_content)
    logging.info("project published")
