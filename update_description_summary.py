from pathlib import Path

import update_description
import update_summary


def main(
    path_summary_top: Path,
    folder_path_output: Path,
    document_hashtag,
    document_title,
):
    list_file_path_zip = update_description.get_list_file_path_zip(
        folder_path_output
    )

    count_file_path_zip = len(list_file_path_zip)
    if count_file_path_zip == 0:
        return

    update_description.descriptions_report_update_with_docs(
        folder_path_output, list_file_path_zip, document_hashtag
    )
    count_file_path_zip = len(list_file_path_zip)
    update_summary.summary_text_update_with_docs(
        count_file_path_zip,
        path_summary_top,
        folder_path_output,
        document_hashtag,
        document_title,
    )
