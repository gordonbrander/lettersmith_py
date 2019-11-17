"""
Tools for building pagination.
"""
from lettersmith.util import chunk, expand
from lettersmith import doc as Doc
from lettersmith.util import composable


TEMPLATES = ("list.html", "default.html")


@composable
def paginate(docs,
    templates=tuple(),
    output_path_template="page/{n}/index.html",
    per_page=25
):
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