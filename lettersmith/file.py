"""
File utilities
"""
from os import path, makedirs
import subprocess
from pathlib import Path


def write_file_deep(file_path, content):
    """Write a file to filepath, creating directory if necessary"""
    try:
        dirname = path.dirname(file_path)
        makedirs(dirname)
    except:
        pass

    with open(file_path, "w") as f:
        f.write(content)


def _copy_dir(input_path, output_path, recursive=True, content=True):
    """
    Copies a directory at `input_path` to `output_path`.
    """
    input_path = Path(input_path)
    input_path_str = str(input_path) + "/" if content else str(input_path)
    if recursive:
        cmd = ("rsync", "-r", input_path_str, str(output_path))
    else:
        cmd = ("rsync", input_path_str, str(output_path))
    return subprocess.run(cmd, check=True)


def copy(input_path, output_path, recursive=True, content=False):
    """
    Copies a file or directory to `output_path`. Uses `cp` under the hood.

    If `input_path` is a directory and `recursive` is True, will copy
    recursively.

    If `input_path` is a directory and ends with a trailing slash, content
    will be copied, rather than directory itself.
    """
    input_path = Path(input_path)
    if input_path.is_dir():
        return _copy_dir(
            input_path, output_path,
            recursive=recursive, content=content)
    else:
        cmd = ("cp", str(input_path), str(output_path))
        return subprocess.run(cmd, check=True)


def copy_all(input_paths, output_path, recursive=True):
    """
    Copy an iterable of file and/or directory paths to `output_path`.
    If `recursive` is True, will copy directory content recursively.
    """
    for input_path in input_paths:
        copy(input_path, output_path, recursive)