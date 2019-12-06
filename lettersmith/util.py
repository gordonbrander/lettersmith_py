"""
Utility functions.
Mostly tools for working with dictionaries and iterables.
"""
from functools import wraps
from fnmatch import fnmatch
from collections import OrderedDict


def chunk(iterable, n):
    """
    Split an iterable into chunks of size n.
    Returns an iterator of sequences.
    """
    chunk = []
    for x in iterable:
        chunk.append(x)
        if len(chunk) == n:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk


def mix(d, e):
    """
    Combine two dicts.
    Just a function version of the spread operator for dicts.
    """
    return {**d, **e}


def _first(pair):
    return pair[0]


def order_dict_by_keys(d):
    """
    Create an OrderedDict, ordered by key asc.
    """
    return OrderedDict(sorted(
        d.items(),
        key=_first
    ))


def join(words, sep="", template="{word}"):
    """
    Join an iterable of strings, with optional template string defining
    how each word is to be templated before joining.
    """
    return sep.join(template.format(word=word) for word in words)


def expand(f, iter, *args, **kwargs):
    """
    Expand each item in `iter` using function `f`.
    `f` is expected to return an iterator itself... it "expands"
    each item.
    """
    for x in iter:
        for y in f(x, *args, **kwargs):
            yield y


def index_sets(items):
    """
    Create a dictionary of sets from an iterable of `(key, value)` pairs.

    Each item is stored in a set at `key`. More than one item with same key
    means items get appended to same list.

    This means items in indices are unique, but they must be hashable.
    """
    index = {}
    for key, value in items:
        try:
            index[key].add(value)
        except KeyError:
            index[key] = set((value,))
    return index


def index_many(items):
    """
    Create a dictionary of lists from an iterable of `(key, value)` pairs.

    Each item is stored in a list at `key`. More than one item with same key
    means items get appended to same list.
    """
    index = {}
    for key, value in items:
        try:
            index[key].append(value)
        except KeyError:
            index[key] = [value]
    return index
