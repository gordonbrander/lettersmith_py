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
        "section": doc.section,
        "name": id_path.name,
        "stem": id_path.stem,
        "suffix": id_path.suffix,
        "parents": str(id_path.parent),
        "parent": id_path.parent.stem,
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
    Update permalinks on docs.

    `config` is a dictionary, where keys are doc sections, and values
    are permalink templates.
    """
    return query.maps(doc_permalink(permalink_template))


post_permalink = permalink("{yyyy}/{mm}/{dd}/{stem}/index.html")
page_permalink = compose(with_ext_html, nice_path)


def rel_page_permalink(tlds):
    return compose(with_ext_html, nice_path, relative_to(tlds))