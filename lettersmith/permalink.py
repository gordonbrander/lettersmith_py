from pathlib import PurePath

from lettersmith.util import put

def read_doc_permalink(doc):
    """
    Read doc, producing a flat dictionary of permalink template token values.
    """
    id_path = PurePath(doc["id_path"])
    return {
        "section": doc["section"],
        "name": id_path.name,
        "stem": id_path.stem,
        "suffix": id_path.suffix,
        "parents": str(id_path.parent),
        "parent": id_path.parent.stem,
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
    try:
        path_template = path_template_map[doc["section"]]
        output_path = path_template.format(**read_doc_permalink(doc))
        output_path = str(PurePath(output_path))
        return put(doc, "output_path", output_path)
    except KeyError:
        return doc


def map_permalink(docs, path_template_map):
    """
    Map doc permalinks, returning a generator that will yield docs with
    permalinks adhering to the templates given in `path_template_map`.

    `path_template_map` is a dictionary of section/template pairs, where
    any doc with a given section will be mapped with the associated
    permalink template.
    """
    return (update_output_path(doc, path_template_map) for doc in docs)