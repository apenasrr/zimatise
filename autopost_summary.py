import asyncio
import os
import time
from pathlib import Path

import tgsender
import vidtool

import utils


def get_chat_id(folder_path_summary: Path):
    file_path_metadata = (folder_path_summary / "channel_metadata").absolute()
    if file_path_metadata.exists():
        dict_metadata = eval(utils.get_txt_content(file_path_metadata))
        chat_id = dict_metadata["chat_id"]
    else:
        raise Exception(
            "No metadata file found. Make sure the channel was created"
        )
    return chat_id


def break_line_max_carac(stringa: str, max_lenght: int) -> list:
    """Breaks a long sentence into chunks of sentences with a maximum length.

    Args:
        stringa (str): The input sentence.
        max_carac (int): The maximum length of each chunk.

    Returns:
        list: A list of sentence chunks.

    """

    list_word = stringa.split(" ")
    list_chunk = []
    chunk = []
    for word in list_word:
        future_state = " ".join(chunk + [word])
        if len(future_state) > max_lenght:
            list_chunk.append(" ".join(chunk))
            chunk = []
        chunk.append(word)

    if chunk:
        list_chunk.append(" ".join(chunk))

    return list_chunk


def get_list_content(content: str) -> list:
    """Split content into blocks of up to 4000 characters.
    Use line breaks as separators. If a line surpasses the limit, it is divided
    into smaller pieces using space as separators.

    Args:
        content (str): content

    Returns:
        list: list of content limited to 4000 characters
    """

    max_lenght = 4000
    if len(content) > max_lenght:
        list_line = content.split("\n")
        bucket = []
        list_content = []
        for line in list_line:
            # Test if with the inclusion of the new line,
            # extrapolates the limit character
            future_bucket_state = "\n".join(bucket + [line])
            if len(future_bucket_state) < max_lenght:
                # If it does not exceed, throw line in the bucket
                bucket.append(line)
            else:
                # If it exceed, save the current state of the bucket
                list_content.append("\n".join(bucket))
                bucket = []
                # and check if line exceeds the limit
                if len(line) < max_lenght:
                    # If it does not exceed, throw line in the bucket
                    bucket.append(line)
                else:
                    # If it exceed, break the line in small sentenses and save
                    # each piece as independent content
                    list_sentense = break_line_max_carac(line, max_lenght)
                    list_content += list_sentense
        if len(bucket) > 0:
            list_content.append("\n".join(bucket))
    else:
        list_content = [content]

    return list_content


def send_summary(chat_id, summary_content):
    list_content = get_list_content(summary_content)
    for index, content in enumerate(list_content):
        message_obj = asyncio.run(
            tgsender.api_async.send_message(chat_id, content)
        )
        if index == 0:
            first_message_id = message_obj.id
    return first_message_id


def get_summary_content(folder_path_summary: Path) -> str:
    file_path_summary = folder_path_summary / "summary.txt"
    summary_content = utils.get_txt_content(file_path_summary)
    return summary_content


def pin_summary_post(chat_id, summary_post_id):
    asyncio.run(tgsender.api_async.pin_chat_message(chat_id, summary_post_id))


def run(folder_path_summary: Path):
    """Post and Pin the summary content

    Args:
        folder_path_summary (Path): folder path of the summary file
    """

    summary_content = get_summary_content(folder_path_summary)
    chat_id = get_chat_id(folder_path_summary)
    summary_post_id = send_summary(chat_id, summary_content)
    time.sleep(5)
    pin_summary_post(chat_id, summary_post_id)


def main(folder_path_project: Path):
    file_path_report = vidtool.set_path_file_report(folder_path_project)
    folder_path_report = file_path_report.parent

    run(folder_path_report)


if __name__ == "__main__":
    main()
