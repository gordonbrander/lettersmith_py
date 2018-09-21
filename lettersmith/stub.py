from datetime import datetime
from pathlib import PurePath
from collections import namedtuple
import frontmatter
from lettersmith.util import replace, get
from lettersmith import path as pathtools
from lettersmith.date import EPOCH
from lettersmith.stringtools import truncate, strip_html

Stub = namedtuple("Stub", (
    "id_path", "output_path", "input_path",
    "created", "modified",
    "title", "summary", "section",
    "meta"
))
Stub.__doc__ = """
Stubs are namedtuples that represent stub documents.
Stubs are meant to be small, so that many can be collected in memory
for cross-referencing via meta information.

Once you're finished building indexes it's typical to transform these
stubs into docs with `lettersmith.doc.load_stub`.
"""


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


@get.register(Stub)
def get_doc(doc, key, default=None):
    return getattr(doc, key, default)


@replace.register(Stub)
def replace_stub(stub, **kwargs):
    """
    Replace items in a Stub, returning a new Stub.
    """
    return stub._replace(**kwargs)


def from_doc(doc, max_len=250, suffix="..."):
    try:
        summary = doc.meta["summary"]
    except KeyError:
        summary = truncate(strip_html(doc.content), max_len, suffix)

    return stub(
        id_path=doc.id_path,
        output_path=doc.output_path,
        input_path=doc.input_path,
        created=doc.created,
        modified=doc.modified,
        title=doc.title,
        summary=summary,
        section=doc.section,
        meta=doc.meta
    )

