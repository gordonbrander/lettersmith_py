"""
Stubs are summary details for a document.
"""
from collections import namedtuple
from lettersmith import doc as Doc
from lettersmith import lens


Stub = namedtuple("Stub", (
    "id_path",
    "output_path",
    "title",
    "summary"
))
Stub.__doc__ = """
A namedtuple for representing a stub. A stub is just a container for
the summary details of a document. No content, no meta.
"""

def from_doc(doc):
    """
    Read link from doc
    """
    return Stub(
        lens.get(Doc.id_path, doc),
        lens.get(Doc.output_path, doc),
        lens.get(Doc.title, doc),
        lens.get(Doc.meta_summary, doc)
    )