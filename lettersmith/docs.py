"""
Tools for working with collections of docs
"""
from pathlib import Path
from itertools import islice
from fnmatch import fnmatch
import shutil
from lettersmith import path as pathtools
from lettersmith import doc as Doc
from lettersmith import query
from lettersmith.func import composable, compose
from lettersmith.lens import every, over


def load(file_paths, relative_to=""):
    """
    Given an iterable of file paths, create an iterable of loaded docs.
    Ignores special files.
    """
    for path in file_paths:
        if pathtools.is_doc_file(path):
            yield Doc.load(path, relative_to=relative_to)


def find(input_path, glob):
    """
    Load all docs under input path that match a glob pattern.

    Example:

        Docs.load_matching("posts", "*.md")
    """
    return load(Path(input_path).glob(glob), relative_to=input_path)


def write(docs, output_path="public"):
    """
    Consume an iterable of docs, writing them as files.
    """
    # Remove output path
    shutil.rmtree(output_path, ignore_errors=True)
    written = 0
    for doc in docs:
        written = written + 1
        Doc.write(doc, output_path)
    return {"written": written}


@composable
def remove_id_path(docs, id_path):
    """
    Remove docs with a given id_path.
    """
    for doc in docs:
        if doc.id_path != id_path:
            yield doc


@composable
def matching(docs, glob):
    """
    Filter an iterator of docs to only those docs whos id_path
    matches a unix-style glob pattern.
    """
    for doc in docs:
        if fnmatch(doc.id_path, glob):
            yield doc


@composable
def filter_siblings(docs, id_path):
    """
    Filter a list of dicts with `id_path`, returning a generator
    yielding only those dicts who's id_path is a sibling to
    `id_path`.
    """
    return (
        doc for doc in docs
        if pathtools.is_sibling(id_path, doc.id_path))


remove_drafts = query.rejects(compose(pathtools.is_draft, Doc.id_path.get))
remove_index = query.rejects(compose(pathtools.is_index, Doc.id_path.get))
dedupe = query.dedupes(Doc.id_path.get)
uplift_frontmatter = query.maps(Doc.uplift_frontmatter)
sort_by_created = query.sorts(Doc.created.get, reverse=True)
sort_by_modified = query.sorts(Doc.modified.get, reverse=True)
sort_by_title = query.sorts(Doc.title.get)


def most_recent(n):
    """
    Get most recent `n` docs, ordered by created.
    """
    return compose(
        query.takes(n),
        sort_by_created
    )


def ext_html(docs):
    return every(Doc.output_path, pathtools.ext_html, docs)


def renderer(render):
    """
    Create a renderer for docs using a string render function.

    Can be used as a decorator.
    """
    @Doc.annotate_exceptions
    def render_doc(doc):
        return over(Doc.content, render, doc)
    return query.maps(render_doc)