"""
Tools for querying data structures. Kind of a lightweight LINQ.
"""
from lettersmith.func import compose_ltr


def attr(key, default=None):
    """
    Create a getter for an object attribute
    """
    return lambda obj: getattr(obj, key, default)


def key(key, default=None):
    """
    Create a getter for an object attribute
    """
    return lambda d: d.get(key, default)


def first(indexable):
    """
    Get first item in an indexable object
    """
    return indexable[0]


def gt(y):
    """
    Greater than value?
    """
    return lambda x: x > y


def lt(y):
    """
    Less than value?
    """
    return lambda x: x < y


def eq(y):
    """
    Is equal to value?
    """
    return lambda x: x == y


def neq(y):
    """
    Isn't equal to value?
    """
    return lambda x: x != y


def has(small):
    """
    Does `big` contain `small`?
    """
    return lambda big: big and small in big


def has_any(*smalls):
    """
    Does `big` contain any of the values in `small`?
    """
    def _has_any(big):
        for small in smalls:
            if big and small in big:
                return True
        return False
    return _has_any


def id_path(doc):
    """
    Get doc id_path
    """
    return doc.id_path


def output_path(doc):
    """
    Get doc output_path
    """
    return doc.output_path


def title(doc):
    """
    Get doc title
    """
    return doc.title


def section(doc):
    """
    Get doc section
    """
    return doc.section


def created(doc):
    """
    Get doc created
    """
    return doc.created


def modified(doc):
    """
    Get doc modified
    """
    return doc.modified


def meta(doc):
    """
    Get doc meta
    """
    return doc.meta


def selectf(get):
    """
    Create a mapping function using a getter fn.
    """
    def select(iterable):
        for item in iterable:
            yield get(item)
    return select


def select(iterable, *getters):
    """
    Map iterable with getters.
    """
    f = selectf(compose_ltr(*getters))
    return f(iterable)


def wheref(get):
    """
    Create a filter function using a getter.
    """
    def where(iterable):
        for item in iterable:
            if get(item):
                yield item
    return where


def where(iterable, *getters):
    """
    Filter iterable using getters to test values.
    """
    f = wheref(compose_ltr(*getters))
    return f(iterable)


def sortf(get):
    """
    Create a sorting function using a getter.
    """
    def sortby(iterable, reverse=False):
        return sorted(iterable, key=get, reverse=reverse)
    return sortby


def sort(iterable, *getters, reverse=False):
    """
    Sort using a sequence of getters
    """
    f = sortf(compose_ltr(*getters))
    return f(iterable, reverse=False)