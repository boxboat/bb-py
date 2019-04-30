#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

from io import open
import yaml
import os


def get_files_in_directory(path, absolute, recursive=True):
    """Read a directory and return a list of filenames

    Parameters
    ----------
        directory: `path`
            directory path
        absolute: `bool`
            True if absolute file path is desired
        recursive: `bool`
            default True
    Returns
    -------
    `list` of absolute path filenames
    """
    file_list = []
    if absolute:
        path = os.path.abspath(path)
    if os.path.isdir(path) and recursive:
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                file_list.append(os.path.join(root, filename))
    elif os.path.isdir(path):
        file_list = [
            os.path.join(path, f) for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
    else:
        raise Exception('%s is not a directory', path)
    return file_list


def read_yaml_file(filename):
    """Read yaml file and return python object

    Parameters
    ----------
        filename: `file`
            yaml file to open and parse
    Returns
    -------
    yaml `dict`
    """
    with open(filename, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.FullLoader)
        except Exception as e:
            raise e
