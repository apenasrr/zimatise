import asyncio
import logging
import os
from pathlib import Path
from time import sleep

import tgsender

from utils import compile_template, get_txt_content


def send_showcase_text(list_moc_chat_id: list, showcase_content: str):
    for moc_chat_id in list_moc_chat_id:
        asyncio.run(
            tgsender.api_async.send_message(
                chat_id=moc_chat_id, text=showcase_content
            )
        )
        if len(list_moc_chat_id) > 1:
            sleep(10)


def send_showcase_photo(
    list_moc_chat_id: list, showcase_content: str, cover_path: Path
):
    for moc_chat_id in list_moc_chat_id:
        asyncio.run(
            tgsender.api_async.send_photo(
                chat_id=moc_chat_id,
                file_path=str(cover_path),
                caption=showcase_content,
            )
        )
        if len(list_moc_chat_id) > 1:
            sleep(10)


def get_description(folder_path_project: str) -> str:
    """Get project description text with 500 caracters max lenght

    Args:
        folder_path_project (str): project folder path

    Returns:
        str: description text with 500 caracters max lenght
    """

    max_len = 500
    description_path = Path(folder_path_project) / "description.txt"
    if description_path.exists():
        content = get_txt_content(description_path).replace("\n", " ")
        if len(content) > max_len:
            content = content[:max_len] + "(...)"
    else:
        content = ""
    return content


def get_chat_invite_link(folder_path_project: str):
    file_path_metadata = Path(folder_path_project) / "channel_metadata"
    if file_path_metadata.exists():
        dict_metadata = eval(get_txt_content(file_path_metadata))
        chat_invite_link = dict_metadata["chat_invite_link"]
        return chat_invite_link
    else:
        raise Exception(
            "No metadata file found. Make sure the channel was created"
        )


def get_header_content(folder_path_project: Path):
    """captures the content of the project header

    Args:
        folder_path_project (Path): Project Analysis Folder Path
    """

    file_path_header = folder_path_project / "header_project.txt"
    header_content = get_txt_content(file_path_header)
    return header_content


def showcase_formater(
    template_moc: str, content: str, chat_invite_link: str, description: str
):
    d_keys = {"header_chat": content}
    header_content_raw1 = compile_template(
        d_keys, template_content=template_moc
    )

    header_content_raw2 = "\n".join(header_content_raw1.split("\n")[2:])

    d_keys = {"chat_invite_link": chat_invite_link}
    showcase_content_raw3 = compile_template(
        d_keys, template_content=header_content_raw2
    )

    d_keys = {"description": description}
    showcase_content = compile_template(
        d_keys, template_content=showcase_content_raw3
    )
    return showcase_content


def pipe_publish(
    list_moc_chat_id: list,
    file_path_template_moc: str,
    folder_path_report: str,
    folder_path_project: str,
):
    """Publishes the project info on the map of content (MOC) chat

    Args:
        list_moc_chat_id (list[int]): list of chat_id of MOC
        file_path_template_moc (str): MapOfContent template file path
        folder_path_report (str): Project Analysis Folder Path
        folder_path_project (str): Project folder
    """

    chat_invite_link = get_chat_invite_link(folder_path_report)
    description = get_description(folder_path_project)
    header_content = get_header_content(folder_path_report)
    template_moc = get_txt_content(file_path_template_moc)
    showcase_content = showcase_formater(
        template_moc, header_content, chat_invite_link, description
    )

    cover_path = find_extra("cover", Path(folder_path_project))
    if cover_path:
        send_showcase_photo(list_moc_chat_id, showcase_content, cover_path)
    else:
        send_showcase_text(list_moc_chat_id, showcase_content)
    logging.info("project published")


def find_extra(extra_name: str, folder_path_project: Path) -> Path:
    """Find a file by name regardless of the extension in a folder

    Args:
        extra_name (str): file name without extension
        folder_path_project (Path): folder path

    Returns:
        Path: file path found
    """

    list_found = [
        x for x in folder_path_project.iterdir() if x.stem == extra_name
    ]
    if len(list_found) != 0:
        if len(list_found) > 1:
            print(f"Multiple {extra_name}s found.")
        extra_path = list_found[0]
    else:
        extra_path = None
    return extra_path
