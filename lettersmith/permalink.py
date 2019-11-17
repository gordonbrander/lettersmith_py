from pathlib import PurePath
from lettersmith.docs import ext_html
from lettersmith.util import composable, compose
from lettersmith import path as pathtools


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


def replace_doc_permalink(doc, permalink_templates):
    """
    Given a doc dict and a permalink template, render
    the output_path field of the doc.

    `permalink_templates` is a dictionary of section/template pairs, where
    any doc with a given section will be mapped with the associated
    permalink template.
    """
    try:
        path_template = permalink_templates[doc.section]
        output_path = path_template.format(**read_doc_permalink(doc))
        output_path = str(PurePath(output_path))
        return doc._replace(output_path=output_path)
    except KeyError:
        return doc


def nice_path(docs):
    """
    Change document paths to nice paths.

    E.g. "foo.html" becomes "foo/index.html" so you have nice URLS.

    This is a simple kind of permalink transform. If you want more
    control over permalink output, use replace_permalinks.
    """
    for doc in docs:
        yield doc._replace(
            output_path=pathtools.to_nice_path(doc.output_path)
        )


@composable
def permalink(docs, permalink_template):
    """
    Update permalinks on docs.

    `config` is a dictionary, where keys are doc sections, and values
    are permalink templates.
    """
    for doc in docs:
        yield replace_doc_permalink(doc, permalink_templates)


post_permalink = permalink("{yyyy}/{mm}/{dd}/{name}/index.html")
page_permalink = compose(ext_html, nice_path)

