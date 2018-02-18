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
    return (
        Doc.load(x, relative_to=relative_to)
        for x in file_paths
        if is_doc_file(x)
    )


def load_json(file_paths, relative_to=""):
    """
    Given an iterable of file paths, create an iterable of loaded docs.
    Ignores special files.
    """
    return (
        Doc.load_json(x, relative_to=relative_to)
        for x in file_paths
        if is_doc_file(x)
    )


def load_yaml(file_paths, relative_to=""):
    """
    Given an iterable of file paths, create an iterable of loaded docs.
    Ignores special files.
    """
    return (
        Doc.load_yaml(x, relative_to=relative_to)
        for x in file_paths
        if is_doc_file(x)
    )


def remove_drafts(docs):
    return (doc for doc in docs if not is_draft(doc["simple_path"]))


def remove_index(docs):
    """
    Filter index from docs
    """
    return (doc for doc in docs if not is_index(doc["simple_path"]))


def filter_siblings(docs, simple_path):
    """
    Filter a list of dicts with `simple_path`, returning a generator
    yielding only those dicts who's simple_path is a sibling to
    `simple_path`.
    """
    return (
        doc for doc in docs
        if pathtools.is_sibling(simple_path, doc["simple_path"]))


def reduce_index(docs):
    """
    Build li index. This is just a dict of summarized docs.
    """
    return {doc["simple_path"]: Doc.to_li(doc) for doc in docs}


def write(docs, output_path="public"):
    """
    Consume an iterable of docs, writing them as files.
    """
    written = 0
    for doc in docs:
        written = written + 1
        Doc.write(doc, output_path)
    return {"written": written}