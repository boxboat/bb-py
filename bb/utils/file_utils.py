#
# 2018 Copyright BoxBoat Technologies
# All Rights Reserved
#
# Author: Matthew DeVenny
#

from io import open
import yaml


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
            return yaml.load(stream)
        except Exception as e:
            raise e
