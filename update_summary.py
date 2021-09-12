import os
import shutil
import utils


def get_summary_text_docs(document_title,
                          document_hashtag,
                          count_file_path_zip):

    str_hashtag_concat = ''
    for index in range(count_file_path_zip):
        if index == 0:
            str_hashtag_concat = f'#{document_hashtag}{index+1:03}'
        else:
            str_hashtag_concat = (str_hashtag_concat +
                                  f'; #{document_hashtag}{index+1:03}')
    str_summary_text_docs = f'{document_title}\n{str_hashtag_concat}'
    return str_summary_text_docs


def get_summary_content_update(folder_path_output, path_summary_top,
                               str_summary_text_docs):

    path_summary = os.path.join(folder_path_output, 'summary.txt')
    summary_content = utils.get_txt_content(path_summary)

    summary_top_content = utils.get_txt_content(path_summary_top)
    len_summary_top_content = len(summary_top_content)

    summary_split_content_1 = summary_content[:len_summary_top_content]
    summary_split_content_2 = summary_content[len_summary_top_content:].strip()
    summary_content_update = \
        (f'{summary_split_content_1}\n' +
         f'{str_summary_text_docs}\n' +
         '\n' +
         f'{summary_split_content_2}')

    return summary_content_update


def save_summary_updated(folder_path_output, summary_content_update):

    # backup
    path_file_summary = os.path.join(folder_path_output, 'summary.txt')
    path_file_summary_to = os.path.join(folder_path_output,
                                        'summary-only_videos.txt')
    shutil.copy(path_file_summary, path_file_summary_to)

    # save
    utils.create_txt(path_file_summary, summary_content_update)


def summary_text_update_with_docs(count_file_path_zip,
                                  path_summary_top,
                                  folder_path_output,
                                  document_hashtag,
                                  document_title):

    str_summary_text_docs = get_summary_text_docs(document_title,
                                                  document_hashtag,
                                                  count_file_path_zip)

    summary_content_update = get_summary_content_update(folder_path_output,
                                                        path_summary_top,
                                                        str_summary_text_docs)
    save_summary_updated(folder_path_output, summary_content_update)
