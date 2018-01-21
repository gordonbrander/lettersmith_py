from pathlib import Path
import yaml
from lettersmith.path import glob_all


YAML_EXT = (".yaml", ".yml")
JSON_EXT = (".json")


def _smart_read_data_file(file_path):
    """
    Given an open file object, this function will do its best to
    interpret structured data.

    Supported types:

    * .json
    * .yaml
    * .lson: Line-delimeted json. Each line is a discrete JSON blob.
      This function will also attempt to read .txt as line-delimeted JSON.
      See https://en.wikipedia.org/wiki/JSON_Streaming#Line_delimited_JSON.
    """
    ext = Path(file_path).suffix
    with open(file_path, "r") as f:
        if ext in JSON_EXT:
            return json.load(f)
        elif ext in YAML_EXT:
            return yaml.load(f)
        else:
            raise ValueError("Unsupported file type: {}".format(ext))


def load_data_files(dir_path):
    """
    Create a data dictionary for the template. Each file in the list
    will be loaded (supported types include JSON, YAML). The structured
    data will be stored under a key corresponding to the filename
    (without extension).

    Returns a dictionary of structured Python data.
    """
    data = {}
    for file_path in glob_all(dir_path, ("*.yaml", "*.yml", "*.json")):
        try:
            stem = Path(file_path).stem
            data[stem] = _smart_read_data_file(file_path)
        except ValueError:
            pass
    return data