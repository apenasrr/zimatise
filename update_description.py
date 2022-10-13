import os
import shutil

import pandas as pd


def get_list_zips_file_path(folder_path):

    list_file_path_zip = []
    for root, _, files in os.walk(folder_path):
        for file_ in files:
            file_lower = file_.lower()
            if (
                file_lower.endswith(tuple([".zip", ".rar", ".7z"]))
                or ".zip" in file_lower
            ):
                file_path_zip = os.path.join(root, file_)
                list_file_path_zip.append(file_path_zip)
    return list_file_path_zip


def get_list_dict(list_file_path_zip, document_hashtag):

    l = []
    for index, file_path in enumerate(list_file_path_zip):
        d = {}
        index_str = f"{index+1:03}"
        file_name = os.path.basename(file_path)
        d["file_output"] = file_path
        d["description"] = f"#{document_hashtag}{index_str}\n\n{file_name}"
        d["warning"] = ""
        l.append(d)
    return l


def get_df_desc_docs(dict_description_docs):

    df = pd.DataFrame(dict_description_docs)
    return df


def get_df_description_original(folder_path_output):

    path_file_description = os.path.join(folder_path_output, "upload_plan.csv")
    df_desc = pd.read_csv(path_file_description)
    return df_desc


def save_desc_updated(folder_path_output, df_desc_update):

    path_file_description = os.path.join(folder_path_output, "upload_plan.csv")
    # backup
    path_file_description_to = os.path.join(
        folder_path_output, "upload_plan-only_videos.csv"
    )
    shutil.copy(path_file_description, path_file_description_to)

    # save
    df_desc_update.to_csv(path_file_description, index=False)


def descriptions_report_update_with_docs(
    folder_path_output, list_file_path_zip, document_hashtag
):

    dict_description_docs = get_list_dict(list_file_path_zip, document_hashtag)
    df_desc_docs = get_df_desc_docs(dict_description_docs)
    df_desc = get_df_description_original(folder_path_output)
    df_desc_update = pd.concat([df_desc_docs, df_desc], axis=0).reset_index(
        drop=True
    )
    save_desc_updated(folder_path_output, df_desc_update)


def get_list_file_path_zip(folder_path_output):

    folder_path_output_files = os.path.join(
        folder_path_output, "output_videos"
    )
    list_file_path_zip = get_list_zips_file_path(folder_path_output_files)
    return list_file_path_zip
