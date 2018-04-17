from datetime import datetime
from pathlib import PurePath
import frontmatter
from lettersmith import path as pathtools
from lettersmith import doc as Doc


def stub(id_path, output_path,
    input_path=None, created_time=None, modified_time=None,
    title="", summary="", section="", meta=None):
    """
    Create an stub dict, populating it with sensible defaults.

    An stub in the static site collection.
    Stubs are meant to be small, so that many can be collected in memory
    for cross-referencing via meta information.

    Once you're finished building indexes it's typical to transform these
    stub dictionaries into doc dictionaries with `Doc.load_stub`.
    """
    return {
        "id_path": str(id_path),
        "output_path": str(output_path),
        "input_path": str(input_path) if input_path else None,
        "created_time":
            created_time if type(created_time) is datetime else datetime.now(),
        "modified_time":
            modified_time if type(modified_time) is datetime else datetime.now(),
        "title": str(title),
        "summary": str(summary),
        "section": str(section),
        "meta": meta if type(meta) is dict else {},
    }


def to_doc(stub):
    """
    Create a doc dictionary from an stub dictionary.
    This doc dictionary will have an empty "content" field.

    If you want to load a doc from a file stub with an `input_path`,
    use `load_doc` instead.
    """
    return Doc.doc(
        id_path=stub["id_path"],
        output_path=stub["output_path"],
        input_path=stub["input_path"],
        created_time=stub["created_time"],
        modified_time=stub["modified_time"],
        title=stub["title"],
        section=stub["section"],
        meta=stub["meta"]
    )


def load_doc(stub, relative_to=""):
    """
    Loads a doc dictionary from an stub dictionary.

    Returns a dictionary.
    """
    with open(stub["input_path"]) as f:
        _, content = frontmatter.parse(f.read())
        return Doc.doc(
            id_path=stub["id_path"],
            output_path=stub["output_path"],
            input_path=stub["input_path"],
            created_time=stub["created_time"],
            modified_time=stub["modified_time"],
            title=stub["title"],
            section=stub["section"],
            meta=stub["meta"],
            content=content
        )