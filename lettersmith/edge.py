"""
Data structure for describing directed graph connections.
"""
from collections import namedtuple


Edge = namedtuple("Edge", ("tail", "head"))
Edge.__doc__ = """
A directed edge that points from one thing to another.
If you imagine an arrow, tail is the base of the arrow, and head is
the pointy arrow head.
"""