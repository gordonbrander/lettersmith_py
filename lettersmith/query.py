"""
Tools for querying data structures. Kind of a lightweight LINQ.
"""
from itertools import islice
from random import sample


def filters(predicate):
    """
    Keep items if they pass predicate function test.
    """
    return lambda iterable: filter(predicate, iterable)


def rejects(predicate):
    """
    Reject items if they pass predicate function test.
    Inverse of filter.
    """
    def reject(iterable):
        for item in iterable:
            if not predicate(item):
                yield item
    return reject


def maps(a2b):
    """
    Map `iterable` with function `a2b`.
    """
    return lambda iterable: map(a2b, iterable)


def sorts(key=None, reverse=False):
    """
    Sort `iterable` by key.
    """
    return lambda iterable: sorted(iterable, key=key, reverse=reverse)


def takes(n):
    """
    Take `n` elements from `iterable`.
    """
    return lambda iterable: islice(iterable, n)


def samples(k):
    """
    Sample `k` elements at random from `iterable`.
    """
    return lambda iterable: sample(iterable, k)


def dedupes(key):
    """
    De-duplicate items in an iterable by key, retaining order.
    """
    def dedupe(iterable):
        seen = set()
        for item in iterable:
            k = key(item)
            if k not in seen:
                seen.add(k)
                yield item
    return dedupe