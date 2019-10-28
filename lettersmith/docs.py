"""
Tools for working with collections of docs
"""
from pathlib import Path
from itertools import islice
from fnmatch import fnmatch
from lettersmith.path import is_draft, is_index, is_doc_file
from lettersmith import doc as Doc
from lettersmith import util


def load(file_paths, relative_to=""):
    """
    Given an iterable of file paths, create an iterable of loaded docs.
    Ignores special files.
    """
    for path in file_paths:
        if is_doc_file(path):
            yield Doc.load(path, relative_to=relative_to)

def load_matching(input_path, glob):
    """
    Load all docs under input path that match a glob pattern.

    Example:

        Docs.glob("posts", "*.md")
    """
    return load(Path(input_path).glob(glob), relative_to=input_path)


def write(docs, output_path="public"):
    """
    Consume an iterable of docs, writing them as files.
    """
    written = 0
    for doc in docs:
        written = written + 1
        Doc.write(doc, output_path)
    return {"written": written}


def remove_drafts(docs):
    return (doc for doc in docs if not is_draft(doc.id_path))


def remove_id_path(docs, id_path):
    """
    Remove docs with a given id_path.
    """
    return (doc for doc in docs if doc.id_path != id_path)


def matching(docs, glob):
    """
    Filter an iterator of docs to only those docs whos id_path
    matches a unix-style glob pattern.
    """
    for doc in docs:
        if fnmatch(doc.id_path, glob):
            yield doc


def remove_index(docs):
    """
    Filter index from docs
    """
    return (doc for doc in docs if not is_index(doc.id_path))


def filter_siblings(docs, id_path):
    """
    Filter a list of dicts with `id_path`, returning a generator
    yielding only those dicts who's id_path is a sibling to
    `id_path`.
    """
    return (
        doc for doc in docs
        if pathtools.is_sibling(id_path, doc.id_path))


def most_recent(docs, nitems, reverse=True):
    return islice(util.sort_by(docs, "created", reverse), nitems)


# Mapping versions of single-doc functions.
parse_yaml = util.mapping(Doc.parse_yaml)
parse_json = util.mapping(Doc.parse_json)
change_ext = util.mapping(Doc.change_ext)