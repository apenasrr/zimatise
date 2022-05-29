import os

import pandas as pd


def single_description_summary(folder_path_output, file_path_report_origin):

    # create description
    df = pd.read_excel(file_path_report_origin, engine="openpyxl")
    df_desc = get_df_description_single_mode(df)
    df_desc.to_excel(
        os.path.join(folder_path_output, "descriptions.xlsx"), index=False
    )

    # TODO: create summary


def get_df_description_single_mode(df):

    df_desc = df.loc[:, ["file_path_folder", "file_name", "subfolder_n1"]]
    df_desc["file_output"] = (
        df_desc["file_path_folder"] + "\\" + df_desc["file_name"]
    )
    df_desc["description"] = (
        df_desc["subfolder_n1"] + "\n" + df_desc["file_name"]
    )
    df_desc["warning"] = ""
    df_desc = df_desc.reindex(
        columns=["file_output", "description", "warning"],
    )
    return df_desc
