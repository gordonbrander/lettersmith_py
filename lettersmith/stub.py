"""
Stubs are summary details for a document.
"""
from collections import namedtuple
from lettersmith import doc as Doc
from lettersmith.lens import get
from lettersmith import query


Stub = namedtuple("Stub", (
    "id_path",
    "output_path",
    "created",
    "modified",
    "title",
    "summary"
))
Stub.__doc__ = """
A namedtuple for representing a stub. A stub is just a container for
the summary details of a document. No content, no meta, no template.

Only hashable properties, so stubs can be used in sets.
(Note that datetime objects are immutable and hashable.)
"""

def from_doc(doc):
    """
    Read stub from doc
    """
    return Stub(
        get(Doc.id_path, doc),
        get(Doc.output_path, doc),
        get(Doc.created, doc),
        get(Doc.modified, doc),
        get(Doc.title, doc),
        get(Doc.meta_summary, doc)
    )


stubs = query.maps(from_doc)