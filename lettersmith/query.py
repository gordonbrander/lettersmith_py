"""
Tools for querying data structures. Kind of a lightweight LINQ.
"""
from itertools import islice
from random import sample


def filters(predicate):
    """
    Keep items if they pass predicate function test.
    """
    def filter_bound(iterable):
        """
        Filter iterable with bound predicate function.
        """
        return filter(predicate, iterable)
    return filter_bound


def rejects(predicate):
    """
    Reject items if they pass predicate function test.
    Inverse of filter.
    """
    def reject_bound(iterable):
        """
        Reject items with bound predicate function.
        """
        for item in iterable:
            if not predicate(item):
                yield item
    return reject_bound


def maps(a2b):
    """
    Map `iterable` with function `a2b`.
    """
    def map_bound(iterable):
        """
        Map iterable using bound function.
        """
        return map(a2b, iterable)
    return map_bound


def sorts(key=None, reverse=False):
    """
    Sort `iterable` by key.
    """
    def sort_bound(iterable):
        """
        Sort iterable using bound arguments.
        """
        return sorted(iterable, key=key, reverse=reverse)
    return sort_bound


def takes(n):
    """
    Take `n` elements from `iterable`.
    """
    def take_bound(iterable):
        """
        Return first n elements of iterable.
        """
        return islice(iterable, n)
    return take_bound


def samples(k):
    """
    Sample `k` elements at random from `iterable`.
    """
    def sample_bound(iterable):
        """
        Sample `k` elements at random from `iterable`.
        """
        return sample(iterable, k)
    return sample_bound


def dedupes(key):
    """
    De-duplicate items in an iterable by key, retaining order.
    """
    def dedupe(iterable):
        """
        De-duplicate items in an iterable using bound key function,
        retaining order.
        """
        seen = set()
        for item in iterable:
            k = key(item)
            if k not in seen:
                seen.add(k)
                yield item
    return dedupe