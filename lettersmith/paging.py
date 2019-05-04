"""
Tools for building pagination.
"""
from math import ceil
from itertools import islice, chain
from voluptuous import Schema, Optional
from lettersmith.util import chunk, filter_id_path, expand, compose
from lettersmith import doc as Doc


TEMPLATES = ("list.html", "default.html")


group_schema = Schema({
    "match": str,
    Optional("per_page", default=10): int,
    Optional("templates", default=[]): [str],
    Optional("output_path_template", default="page/{n}/index.html"): str
})


schema = Schema({
    Optional("groups", default=[]): [group_schema]
})


def paginate(docs, templates, output_path_template, per_page):
    """
    Generate paging docs from stubs
    """
    paged = tuple(chunk(docs, per_page))
    page_count = len(paged)
    templates = (*templates, *TEMPLATES)
    n = 0
    for page in paged:
        n = n + 1
        output_path = output_path_template.format(n=n)
        page_list = tuple(doc for doc in page)
        meta = {
            "page_n": n,
            "per_page": per_page,
            "page_count": page_count,
            "page_list": page_list
        }
        yield Doc.doc(
            id_path=output_path,
            output_path=output_path,
            title="Page {}".format(n),
            meta=meta,
            templates=templates
        )


def paging(docs, config):
    """
    Generate paging docs from an iterable of docs, and dictionaries
    of options. Each key of a dictionary represents a group of options
    for a set of pages that should be produced.
    """
    docs = tuple(docs)
    def _expand_group(group):
        matching_docs = filter_id_path(docs, group["match"])
        return paginate(
            matching_docs,
            templates=group["templates"],
            output_path_template=group["output_path_template"],
            per_page=group["per_page"]
        )
    return expand(_expand_group, config["groups"])
