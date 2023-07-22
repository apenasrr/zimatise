import os
import shutil
from pathlib import Path
from typing import List

import pandas as pd


def get_list_zips_file_path(folder_path: Path) -> List[Path]:
    list_file_path_zip = []
    for root, _, files in os.walk(str(folder_path)):
        for file_ in files:
            file_lower = file_.lower()
            if (
                file_lower.endswith(tuple([".zip", ".rar", ".7z"]))
                or ".zip" in file_lower
            ):
                file_path_zip = Path(root) / file_
                list_file_path_zip.append(file_path_zip)
    return list_file_path_zip


def get_list_dict(list_file_path_zip: List[Path], document_hashtag: str):
    l = []
    for index, file_path in enumerate(list_file_path_zip):
        d = {}
        index_str = f"{index+1:03}"
        file_name = file_path.name
        d["file_output"] = str(file_path)
        d["description"] = f"#{document_hashtag}{index_str}\n\n{file_name}"
        d["warning"] = ""
        l.append(d)
    return l


def get_df_desc_docs(dict_description_docs):
    df = pd.DataFrame(dict_description_docs)
    return df


def get_df_description_original(folder_path_output: Path):
    file_path_description = folder_path_output / "upload_plan.csv"
    df_desc = pd.read_csv(file_path_description)
    return df_desc


def save_desc_updated(folder_path_output: Path, df_desc_update):
    file_path_description = folder_path_output / "upload_plan.csv"
    # backup
    file_path_description_to = (
        folder_path_output / "upload_plan-only_videos.csv"
    )
    shutil.copy(file_path_description, file_path_description_to)

    # save
    df_desc_update.to_csv(file_path_description, index=False)


def descriptions_report_update_with_docs(
    folder_path_output: Path, list_file_path_zip: List[Path], document_hashtag
):
    dict_description_docs = get_list_dict(list_file_path_zip, document_hashtag)
    df_desc_docs = get_df_desc_docs(dict_description_docs)
    df_desc = get_df_description_original(folder_path_output)
    df_desc_update = pd.concat([df_desc_docs, df_desc], axis=0).reset_index(
        drop=True
    )
    save_desc_updated(folder_path_output, df_desc_update)


def get_list_file_path_zip(folder_path_output: Path) -> List[Path]:
    folder_path_output_files = folder_path_output / "output_videos"
    list_file_path_zip = get_list_zips_file_path(folder_path_output_files)
    return list_file_path_zip
