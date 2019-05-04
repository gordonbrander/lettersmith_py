"""
Tools for working with link data.
"""
from lettersmith.util import get
from collections import namedtuple


Link = namedtuple("Link", ("id_path", "output_path", "title"))
Link.__doc__ = """
A namedtuple for representing a link entry. Just the basic information
needed to construct a hyperlink.
"""


@get.register(Link)
def get_link(link, key, default=None):
    return getattr(link, key, default)


Edge = namedtuple("Edge", ("tail", "head"))
Edge.__doc__ = """
A directed edge that points from one thing to another.
If you imagine an arrow, tail is the base of the arrow, and head is
the pointy arrow head.
"""