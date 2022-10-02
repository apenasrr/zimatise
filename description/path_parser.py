from collections import defaultdict
from pathlib import Path


def nested_dict():
    """
    Creates a default dictionary where each value is an other default dictionary.
    """
    return defaultdict(nested_dict)


def default_to_regular(d):
    """
    Converts defaultdicts of defaultdicts to dict of dicts.
    """
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def get_tree_directory(list_path):

    new_path_dict = nested_dict()
    for path in list_path:
        parts = Path(path).parts
        if parts:
            marcher = new_path_dict
            for key in parts[:-1]:
                marcher = marcher[key]
            path_to_be_parsed = parts[-1]
            marcher[parts[-1]] = Path(path_to_be_parsed).suffix.strip(".")
    return default_to_regular(new_path_dict)
