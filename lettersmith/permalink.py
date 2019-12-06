from pathlib import PurePath
from lettersmith.docs import with_ext_html
from lettersmith.func import composable, compose
from lettersmith import path as pathtools
from lettersmith.lens import over_with, put
from lettersmith import doc as Doc
from lettersmith import query


def read_doc_permalink(doc):
    """
    Read doc, producing a flat dictionary of permalink template token values.
    """
    id_path = PurePath(doc.id_path)
    return {
        "name": id_path.name,
        "stem": id_path.stem,
        "suffix": id_path.suffix,
        "parents": str(id_path.parent),
        "parent": id_path.parent.stem,
        "tld": Doc.id_tld(doc),
        "yy": doc.created.strftime("%y"),
        "yyyy": doc.created.strftime("%Y"),
        "mm": doc.created.strftime("%m"),
        "dd": doc.created.strftime("%d")
    }


@composable
def doc_permalink(doc, permalink_template):
    """
    Given a doc dict and a permalink template, render
    the output_path field of the doc.
    """
    output_path = permalink_template.format(**read_doc_permalink(doc))
    return put(Doc.output_path, doc, output_path)


def relative_to(tlds):
    """
    Create a function that maps doc output path to be relative
    to some top-level path.
    """
    rel_to_tlds = pathtools.relative_to(tlds)
    return query.maps(over_with(Doc.output_path, rel_to_tlds))


nice_path = query.maps(
    over_with(Doc.output_path, pathtools.to_nice_path)
)


def permalink(permalink_template):
    """
    Set output_path on docs using a python string template.

    For example, here's a typical blog year-based permalink:

        permalink("{yyyy}/{mm}/{dd}/{stem}/index.html")

    Available tokens:

    - name: the doc's file name, including extension (e.g. `name.html`)
    - stem: the doc's file name, sans extension (e.g. `name`)
    - suffix: the doc's file extension (e.g. `.html`)
    - parents: full directory path to the doc, sans file name.
    - parent: the immediate parent directory
    - tld: the top-level directory
    - yy: the 2-digit year
    - yyyy: the 4-digit year
    - mm: the 2-digit month
    - dd: the 2-digit day
    """
    return query.maps(doc_permalink(permalink_template))


post_permalink = permalink("{yyyy}/{mm}/{dd}/{stem}/index.html")
post_permalink.__doc__ = """
Sets typical blog date-based output_path on docs:

    2019/12/01/my-post/index.html
"""

page_permalink = compose(with_ext_html, nice_path)
page_permalink.__doc__ = """
Sets nice path on doc, retaining original directory path, but
giving it a nice URL, and an .html extension.

    path/to/some/file.md

Becomes:

    path/to/some/file/index.html

"""


def rel_page_permalink(tlds):
    """
    Sets nice path that keeps original directory structure, relative to
    some top-level path.

        path/to/some/file.md

    Where `tlds` is "path/to", becomes:

        some/file/index.html
    """
    return compose(with_ext_html, nice_path, relative_to(tlds))