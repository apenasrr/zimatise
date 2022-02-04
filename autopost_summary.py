import os

import utils

utils.add_path_script_folders(["mass_videojoin", "telegram_filesender"])
import api_telegram
import mass_videojoin


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


def send_summary(chat_id, summary_content):

    message_obj = api_telegram.send_message(chat_id, summary_content)
    message_id = message_obj["message_id"]
    return message_id


def get_summary_content(folder_path_summary):

    file_path_summary = os.path.join(folder_path_summary, "summary.txt")
    summary_content = utils.get_txt_content(file_path_summary)
    return summary_content


def pin_summary_post(chat_id, summary_post_id):

    api_telegram.pin_chat_message(chat_id, summary_post_id)


def run(folder_path_summary):
    """Post and Pin the summary content

    Args:
        folder_path_summary (str): folder path of the summary file
    """

    summary_content = get_summary_content(folder_path_summary)
    chat_id = get_chat_id(folder_path_summary)
    summary_post_id = send_summary(chat_id, summary_content)
    pin_summary_post(chat_id, summary_post_id)


def main(folder_path_project):

    file_path_report = mass_videojoin.set_path_file_report(folder_path_project)
    folder_path_report = os.path.dirname(file_path_report)

    run(folder_path_report)


if __name__ == "__main__":
    main()
