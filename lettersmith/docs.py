"""
Tools for working with collections of docs
"""
from itertools import islice
from lettersmith.path import is_draft, is_index, is_doc_file
from lettersmith import doc as Doc
from lettersmith.util import sort_by


def load(file_paths, relative_to=""):
    """
    Given an iterable of file paths, create an iterable of loaded docs.
    Ignores special files.
    """
    for path in file_paths:
        if is_doc_file(path):
            yield Doc.load(path, relative_to=relative_to)


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
    return islice(sort_by(docs, "created", reverse), nitems)