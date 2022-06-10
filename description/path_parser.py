from collections import defaultdict
import os

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

def get_tree_directory(paths):
    new_path_dict = nested_dict()
    for path in paths:
        parts = path.split('\\')
        if parts:
            marcher = new_path_dict
            for key in parts[:-1]:
               marcher = marcher[key]
            marcher[parts[-1]] = os.path.splitext(parts[-1])[1].strip('.')
    return default_to_regular(new_path_dict)