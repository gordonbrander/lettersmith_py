from pathlib import PurePath

from lettersmith.util import put

def read_doc_permalink(doc):
    simple_path = PurePath(doc["simple_path"])
    return {
        "section": doc["section"],
        "name": simple_path.name,
        "stem": simple_path.stem,
        "suffix": simple_path.suffix,
        "parents": str(simple_path.parent),
        "parent": simple_path.parent.stem,
        "yy": doc["date"].strftime("%y"),
        "yyyy": doc["date"].strftime("%Y"),
        "mm": doc["date"].strftime("%m"),
        "dd": doc["date"].strftime("%d")
    }


def update_output_path(doc, path_template_map):
    """
    Given a doc dict and a permalink template, render
    the output_path field of the doc.
    """
    # Run the resulting permalink through urlize. This allows directories
    # to have spaces, etc.
    try:
        path_template = path_template_map[doc["section"]]
        output_path = path_template.format(**read_doc_permalink(doc))
        output_path = str(PurePath(output_path))
        return put(doc, "output_path", output_path)
    except KeyError:
        return doc


def map_permalink(docs, path_template_map):
    return (update_output_path(doc, path_template_map) for doc in docs)