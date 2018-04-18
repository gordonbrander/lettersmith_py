"""
Tools for building pagination.
"""

from math import ceil
from itertools import islice, chain
from lettersmith.util import chunk, get
from lettersmith import doc as Doc


TEMPLATES = ("list.html", "default.html")
OUTPUT_PATH_TEMPLATE = "page/{n}/index.html"


def count_pages(length, per_page):
    """
    Find the number of pages in a list of `length`.
    """
    # Note it's important that we cast to float before division, otherwise
    # we lose floating point precision and get a rounded int.
    return int(ceil(float(length) / float(per_page)))


def slice_page(iterable, page_i, per_page):
    """Slice a page for an iterable"""
    page_start = page_i * per_page
    page_end = page_start + per_page
    return islice(iterable, page_start, page_end)


def prev_i(i):
    return max(i - 1, 0)


def next_i(i, length):
    return min(i + 1, length - 1)


def gen_paging(stubs,
    templates=TEMPLATES,
    output_path_template=OUTPUT_PATH_TEMPLATE,
    per_page=10):
    """
    From an index of lis, produce a generator factory of paging docs.
    """
    paged = tuple(chunk(stubs, per_page))
    page_count = len(paged)
    n = 0
    for stubs in paged:
        n = n + 1
        output_path = output_path_template.format(n=n)
        page_list = tuple(stub for stub in stubs)
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
            meta=meta
        )