"""
File utilities
"""
from os import path, makedirs
import shutil
from pathlib import Path, PurePath


def write_file_deep(pathlike, content):
    """Write a file to filepath, creating directory if necessary"""
    file_path = str(pathlike)
    dirname = path.dirname(file_path)
    makedirs(dirname, exist_ok=True)

    with open(file_path, "w") as f:
        f.write(content)


def copy_dirs(directory_paths, output_directory_path):
    """
    Recursively copy an iterable of directory paths to `output_directory_path`.
    """
    for directory_path in directory_paths:
        input_path = PurePath(directory_path)
        output_path = PurePath(output_directory_path, input_path.name)
        shutil.rmtree(output_path, ignore_errors=True)
        shutil.copytree(input_path, output_path)