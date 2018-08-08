import pickle
from os import makedirs
from pathlib import PurePath


def tee_pickles(iter, file_name, dir_path="."):
    """
    Consumes an iterator and returns a generator for those same items.
    As a side-effect, writes an iterable of objects to pickle files.

    - iter: an iterable of things to pickle.
    - file_name: a function that reads the object to be pickled to generate
      a name for the pickle file.
    - dir_path: a pathlike pointing to the directory in which to write pickle
      files.
    """
    for x in iter:
        full_path = PurePath(dir_path, file_name(x))
        makedirs(full_path.parent, exist_ok=True)
        with open(full_path, "wb") as f:
            pickle.dump(x, f)
            yield x


def dump_pickles(iter, file_name, dir_path=""):
    """
    Same thing as tee_pickles, but immediately consumes the iterable
    and dumps all the iterable items into pickle files.

    Returns None.
    """
    for _ in tee_pickles(iter, file_name, dir_path):
        pass


def load_pickles(file_paths):
    """
    Unpickles an iterable of pathlike objects pointing to Pickle files.
    Returns a generator for the unpickled contents.
    """
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            yield pickle.load(f)