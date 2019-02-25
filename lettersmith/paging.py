"""
Tools for building pagination.
"""

from math import ceil
from itertools import islice, chain
from lettersmith.util import chunk, filter_id_path, expand
from lettersmith import doc as Doc


TEMPLATES = ("list.html", "default.html")
OUTPUT_PATH_TEMPLATE = "page/{n}/index.html"
_EMPTY_TUPLE = tuple()


def paginate(docs,
    templates=_EMPTY_TUPLE,
    output_path_template=OUTPUT_PATH_TEMPLATE,
    per_page=10):
    """
    Generate paging docs from stubs
    """
    paged = tuple(chunk(docs, per_page))
    page_count = len(paged)
    templates = tuple(templates) + TEMPLATES
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


def gen_paging(docs, groups):
    """
    Generate paging docs from an iterable of docs, and dictionary
    of options. Each key of the dictionary represents a group of options
    for a set of pages that should be produced.
    """
    def _expand_pair(pair):
        glob, group = pair
        matching_docs = filter_id_path(docs, glob)
        output_path_template = group.get(
            "output_path_template",
            OUTPUT_PATH_TEMPLATE
        )
        return paginate(
            docs,
            templates=group.get("templates", _EMPTY_TUPLE),
            output_path_template=output_path_template,
            per_page=group.get("per_page", 10)
        )
    return expand(_expand_pair, groups.items())
