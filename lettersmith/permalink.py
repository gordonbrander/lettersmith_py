from pathlib import PurePath
from lettersmith.docs import with_ext_html
from lettersmith.func import composable, compose
from lettersmith import path as pathtools
from lettersmith.lens import over_with
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
        "yy": doc.date.strftime("%y"),
        "yyyy": doc.date.strftime("%Y"),
        "mm": doc.date.strftime("%m"),
        "dd": doc.date.strftime("%d")
    }


def replace_doc_permalink(doc, permalink_template):
    """
    Given a doc dict and a permalink template, render
    the output_path field of the doc.
    """
    try:
        output_path = permalink_template.format(**read_doc_permalink(doc))
        output_path = str(PurePath(output_path))
        return doc._replace(output_path=output_path)
    except KeyError:
        return doc


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


@composable
def permalink(docs, permalink_template):
    """
    Update permalinks on docs.

    `config` is a dictionary, where keys are doc sections, and values
    are permalink templates.
    """
    for doc in docs:
        yield replace_doc_permalink(doc, permalink_template)


post_permalink = permalink("{yyyy}/{mm}/{dd}/{name}/index.html")
page_permalink = compose(with_ext_html, nice_path)

def rel_page_permalink(tlds):
    return compose(with_ext_html, nice_path, relative_to(tlds))