from datetime import datetime
from pathlib import PurePath
from typing import NamedTuple, Union
import frontmatter
from lettersmith.util import replace, get
from lettersmith import path as pathtools
from lettersmith import doc as Doc
from lettersmith.date import EPOCH


class Stub(NamedTuple):
    """
    Stubs are namedtuples that represent stub documents.
    Stubs are meant to be small, so that many can be collected in memory
    for cross-referencing via meta information.

    Once you're finished building indexes it's typical to transform these
    stub dictionaries into doc dictionaries with `Doc.load_stub`.
    """
    id_path: str
    output_path: str
    input_path: Union[str, None]
    created: datetime
    modified: datetime
    title: str
    summary: str
    section: str
    meta: dict


def stub(
    id_path, output_path,
    input_path=None, created=EPOCH, modified=EPOCH,
    title="", summary="", section="", meta=None):
    """
    Create an stub dict, populating it with sensible defaults.
    """
    return Stub(
        id_path=str(id_path),
        output_path=str(output_path),
        input_path=str(input_path) if input_path is not None else None,
        created=created,
        modified=modified,
        title=str(title),
        summary=str(summary),
        section=str(section),
        meta=meta if meta is not None else {}
    )


@replace.register(Stub)
def replace_stub(stub, **kwargs):
    """
    Replace items in a Stub, returning a new Stub.
    """
    return stub._replace(**kwargs)


def to_doc(stub):
    """
    Create a doc dictionary from an stub dictionary.
    This doc dictionary will have an empty "content" field.

    If you want to load a doc from a file stub with an `input_path`,
    use `load_doc` instead.
    """
    return Doc.doc(
        id_path=stub.id_path,
        output_path=stub.output_path,
        input_path=stub.input_path,
        created=stub.created,
        modified=stub.modified,
        title=stub.title,
        section=stub.section,
        meta=stub.meta
    )


def load_doc(stub, relative_to=""):
    """
    Loads a doc dictionary from an stub dictionary.

    Returns a dictionary.
    """
    with open(stub.input_path) as f:
        _, content = frontmatter.parse(f.read())
        return Doc.doc(
            id_path=stub.id_path,
            output_path=stub.output_path,
            input_path=stub.input_path,
            created=stub.created,
            modified=stub.modified,
            title=stub.title,
            section=stub.section,
            content=content,
            meta=stub.meta
        )