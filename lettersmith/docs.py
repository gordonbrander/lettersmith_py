"""
Tools for working with collections of docs
"""
from fnmatch import fnmatch
from lettersmith import path as pathtools
from lettersmith import doc as Doc
from lettersmith import query
from lettersmith.func import composable, compose
from lettersmith.lens import get


load = query.maps(Doc.load)


def find(glob):
    """
    Load all docs under input path that match a glob pattern.

    Example:

        docs.find("posts/*.md")
    """
    return load(pathtools.glob_files(".", glob))


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
    for doc in docs:
        if pathtools.is_sibling(id_path, doc.id_path):
            yield doc


remove_drafts = query.rejects(compose(pathtools.is_draft, Doc.id_path.get))
remove_index = query.rejects(compose(pathtools.is_index, Doc.id_path.get))
dedupe = query.dedupes(Doc.id_path.get)
uplift_frontmatter = query.maps(Doc.uplift_frontmatter)
sort_by_created = query.sorts(Doc.created.get, reverse=True)
sort_by_modified = query.sorts(Doc.modified.get, reverse=True)
sort_by_title = query.sorts(Doc.title.get)
autotemplate = query.maps(Doc.autotemplate)
with_ext_html = query.maps(Doc.with_ext_html)


def most_recent(n):
    """
    Get most recent `n` docs, ordered by created.
    """
    return compose(
        query.takes(n),
        sort_by_created
    )


def with_template(template):
    """
    Set template, but only if doc doesn't have one already.
    """
    return query.maps(Doc.with_template(template))


def renderer(render):
    """
    Create a renderer for docs using a string render function.

    Can be used as a decorator.
    """
    return query.maps(Doc.renderer(render))