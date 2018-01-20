"""
Tools for working with collections of docs
"""
from lettersmith.path import is_draft, is_index, is_doc_file
from lettersmith import doc as Doc


def load(file_paths):
    """
    Given an iterable of fle paths, create an iterable of loaded docs.
    Ignores special files.
    """
    return (Doc.load(x) for x in file_paths if is_doc_file(x))


def remove_drafts(docs):
    return (doc for doc in docs if not is_draft(doc["simple_path"]))


def remove_index(docs):
    """
    Filter index from docs
    """
    return (doc for doc in docs if not is_index(doc["simple_path"]))


# TODO introduce siblings filter


def reduce_li(docs):
    return tuple(Doc.to_li(doc) for doc in docs)


def reduce_index(docs):
    """
    Build list item index
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