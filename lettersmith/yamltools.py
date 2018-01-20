from yaml import load as loads_yaml


def load(file_path):
    """
    Given a file path, read the file contents and parse YAML to
    python dict. Returns a python dict.
    """
    with open(file_path, "r") as f:
        return loads_yaml(f.read())
    return {}


loads = loads_yaml