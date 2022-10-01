import os

from . import single_mode_description, single_mode_summary


def create_txt(file_path, stringa):

    f = open(file_path, "w", encoding="utf8")
    f.write(stringa)
    f.close()


def single_description_summary(
    folder_path_output, file_path_report_origin, dict_summary
):

    # create description
    # df = pd.read_csv(file_path_report_origin)
    df_desc = single_mode_description.create_df_descriptions(
        file_path_report_origin
    )
    description_path = os.path.join(folder_path_output, "upload_plan.csv")
    df_desc.to_csv(description_path, index=False)

    # create summary
    summary_content = single_mode_summary.main(
        file_path_report_origin, dict_summary
    )
    summary_path = os.path.join(folder_path_output, "summary.txt")
    create_txt(summary_path, summary_content)


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
