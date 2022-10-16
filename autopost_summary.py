import asyncio
import os
import time

import tgsender
import vidtool

import utils


def get_chat_id(folder_path_summary):

    file_path_metadata = os.path.realpath(
        os.path.join(folder_path_summary, "channel_metadata")
    )
    if os.path.exists(file_path_metadata):

        dict_metadata = eval(utils.get_txt_content(file_path_metadata))
        chat_id = dict_metadata["chat_id"]
    else:
        raise Exception(
            "No metadata file found. Make sure the channel was created"
        )
    return chat_id


def get_list_content(content: str) -> list:
    """Split content by breakline into blocks of up to 4000 characters

    Args:
        content (str): content

    Returns:
        list: list of content limited to 4000 characters
    """

    if len(content) > 4000:
        list_general_line = content.split("\n")

        list_content = []
        list_block_line = []
        for line in list_general_line:
            new_state = "\n".join(list_block_line) + "\n" + line
            if len(new_state) < 4000:
                list_block_line.append(line)
            else:
                list_content.append("\n".join(list_block_line))
                list_block_line = []
                list_block_line.append(line)

        if len(list_block_line) > 0:
            list_content.append("\n".join(list_block_line))
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


def get_summary_content(folder_path_summary):

    file_path_summary = os.path.join(folder_path_summary, "summary.txt")
    summary_content = utils.get_txt_content(file_path_summary)
    return summary_content


def pin_summary_post(chat_id, summary_post_id):

    asyncio.run(tgsender.api_async.pin_chat_message(chat_id, summary_post_id))


def run(folder_path_summary):
    """Post and Pin the summary content

    Args:
        folder_path_summary (str): folder path of the summary file
    """

    summary_content = get_summary_content(folder_path_summary)
    chat_id = get_chat_id(folder_path_summary)
    summary_post_id = send_summary(chat_id, summary_content)
    time.sleep(5)
    pin_summary_post(chat_id, summary_post_id)


def main(folder_path_project):

    file_path_report = vidtool.set_path_file_report(folder_path_project)
    folder_path_report = os.path.dirname(file_path_report)

    run(folder_path_report)


if __name__ == "__main__":
    main()
