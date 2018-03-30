import os


def path(*paths: str) -> str:
    return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "resources", *paths))


def contents(*paths: str) -> str:
    with open(path(*paths), 'r') as f:
        return f.read()
