"""
Tools for working with collections of docs
"""
from lettersmith.path import is_draft, is_index, is_doc_file
from lettersmith import doc as Doc


def load(file_paths, relative_to=""):
    """
    Given an iterable of file paths, create an iterable of loaded docs.
    Ignores special files.
    """
    for path in file_paths:
        if is_doc_file(path):
            yield Doc.load(path, relative_to=relative_to)


def load_json(file_paths):
    for path in file_paths:
        yield Doc.load_json(path)


def dump_json(docs, dir=""):
    for doc in docs:
        Doc.dump_json(doc, dir)


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