"""
File utilities
"""
from os import path, makedirs
import subprocess
from pathlib import Path


def write_file_deep(file_path, contents):
    """Write a file to filepath, creating directory if necessary"""
    try:
        dirname = path.dirname(file_path)
        makedirs(dirname)
    except:
        pass

    with open(file_path, "w") as f:
        f.write(contents)


def _copy_dir(input_path, output_path, recursive=True, contents=True):
    """
    Copies a directory at `input_path` to `output_path`.
    """
    input_path = Path(input_path)
    input_path_str = str(input_path) + "/" if contents else str(input_path)
    if recursive:
        cmd = ("rsync", "-r", input_path_str, str(output_path))
    else:
        cmd = ("rsync", input_path_str, str(output_path))
    return subprocess.run(cmd, check=True)


def copy(input_path, output_path, recursive=True, contents=False):
    """
    Copies a file or directory to `output_path`. Uses `cp` under the hood.

    If `input_path` is a directory and `recursive` is True, will copy
    recursively.

    If `input_path` is a directory and ends with a trailing slash, contents
    will be copied, rather than directory itself.
    """
    input_path = Path(input_path)
    if input_path.is_dir():
        return _copy_dir(
            input_path, output_path,
            recursive=recursive, contents=contents)
    else:
        cmd = ("cp", str(input_path), str(output_path))
        return subprocess.run(cmd, check=True)


def copy_all(input_paths, output_path, recursive=True):
    for input_path in input_paths:
        copy(input_path, output_path, recursive)