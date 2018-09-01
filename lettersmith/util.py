"""
Utility functions.
Mostly tools for working with dictionaries and iterables.
"""
from functools import reduce, singledispatch
from fnmatch import fnmatch


def id(x):
    """
    The id function.
    """
    return x


def compose2(f, e):
    """Compose 2 functions"""
    return lambda x: f(e(x))


def compose(fn, *fns):
    """Compose n functions"""
    return reduce(compose2, fns, fn)


@singledispatch
def get(x, key, default=None):
    """
    A singledispatch getter function.
    By default, gets attribute (e.g. dot notation).
    """
    raise TypeError("Cannot get entries on unknown type {}".format(x))


@get.register(dict)
def get_dict(d, key, default=None):
    """
    Getter for dictionaries. Does a get on dictionary items
    instead of attributes.
    """
    return d.get(key, default)


def get_deep(d, key, default=None):
    """
    Get a value in a dictionary, or get a deep value in
    nested dictionaries.

    If `keys` is a string, will split on ".".
    If `keys` is an iterable of strings, will attempt to do a deep get.
    If the get fails, will return `default` value.

    Example:

        get_deep(x, "some.deep.key")
        get_deep(x, ("some", "deep", "key"))
    """
    keys = key.split(".") if type(key) is str else tuple(key)
    for key in keys:
        d = get(d, key)
        if d == None:
            return default
    return d


@singledispatch
def replace(x, **kwargs):
    """
    Replace values by keyword argument on some datastructure.
    This is a singledispatch function that can be extended to multiple
    types. Default implementation is provided for dict.
    """
    raise TypeError("Cannot replace entries on unknown type {}".format(x))


@replace.register(dict)
def replace_dict(d, **kwargs):
    """
    Replace values by keyword on a dict, returning a new dict.
    """
    e = d.copy()
    e.update(kwargs)
    return e


def merge(a, b):
    """
    Replace values by keyword on a dict, returning a new dict.
    """
    d = {}
    d.update(a)
    d.update(b)
    return d


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


def id_path_matches(x, match):
    """
    Predicate function that tests whether the id_path of a thing
    (as determined by `get`) matches a glob pattern.
    """
    # We fast-path for "everything" matches.
    return fnmatch(get(x, "id_path"), match) if match != "*" else True


def match_by_id_path(docs, match):
    """
    Filter docs by matching their id_path against a glob pattern.
    """
    for doc in docs:
        if id_path_matches(doc, match):
            yield doc


def decorate_group_matching(predicate):
    def decorate_f(f):
        def f_match_group(iter, groups, defaults={}):
            items = tuple(iter)
            for pattern, kwargs in groups.items():
                matches = tuple(item for item in items if predicate(item, pattern))
                yield f(matches, **replace(defaults, **kwargs))
        f_match_group.inner = f
        return f_match_group
    return decorate_f


decorate_group_matching_id_path = decorate_group_matching(id_path_matches)


_EMPTY_TUPLE = tuple()


def any_in(collection, values):
    """
    Check if any of a collection of values is in `collection`.
    Returns boolean.
    """
    for value in values:
        if value in collection:
            return True
    return False


def contains(x, key, value):
    """
    Check for the inclusion of a value in an indexable in a deep object.
    `key` is a key path (can be a single key or an iterable of keys).
    """
    return value in get_deep(x, key, _EMPTY_TUPLE)


def has_key(x, key):
    """
    Check for the presence of a key in a deep object.
    `key` is a key path (can be a single key or an iterable of keys).
    """
    return get_deep(x, key) != None


def where(dicts, key, value, is_match=True):
    """
    Query an iterable of dictionaries for keys matching value.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in dicts if (get_deep(x, key) == value) == is_match)


def where_not(dicts, key, value, is_match=True):
    """
    Query an iterable of dictionaries for keys not matching value.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in dicts if (get_deep(x, key) == value) != is_match)


def where_key(dicts, key):
    """
    Query an iterable of dictionaries that have `key`.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in dicts if has_key(x, key))


def where_not_key(dicts, key):
    """
    Query an iterable of dictionaries that do NOT have `key`.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in dicts if not has_key(x, key))


def where_contains(dicts, key, value):
    """
    Query an iterable of dictionaries by determining if a `value` is in
    a data structure at `key`. This would be for checking the presence of
    a value within an list that exists at `key`, for example.

    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in dicts if contains(x, key, value))


def where_contains_any(dicts, key, terms):
    """
    Given a list of stubs (or docs), yields any stubs that contain
    any of the terms.
    """
    return (
        x
        for x in dicts
        if any_in(get_deep(x, key, _EMPTY_TUPLE), terms)
    )


def where_matches(dicts, key, glob):
    """
    Query an iterable of dictionaries, matching the value against a
    Unix glob-style pattern.

    Returns an iterable of matching dictionaries.
    """
    return (x for x in dicts if fnmatch(get_deep(x, key), glob))


def lift_iter(f):
    """
    Lift a function to consume an iterator instead of single values.
    """
    def f_iter(iter, *args, **kwargs):
        return (f(x, *args, **kwargs) for x in iter)
    return f_iter


def sort_by(iter_of_dicts, key, reverse=False, default=None):
    """Sort an iterable of dicts via a key path"""
    fkey = lambda x: get(x, key, default=default)
    return sorted(iter_of_dicts, key=fkey, reverse=reverse)


def _first(pair):
    return pair[0]


def sort_items_by_key(items, reverse=False):
    return sorted(
        items,
        key=_first,
        reverse=reverse
    )


def join(words, sep="", template="{word}"):
    """
    Join an iterable of strings, with optional template string defining
    how each word is to be templated before joining.
    """
    return sep.join(template.format(word=word) for word in words)


def tap_each(f, iter):
    """
    Perform a side-effect on each item of an iterable.
    Returns an iterable that must be consumed to perform the
    side-effect.
    """
    for x in iter:
        f(x)
        yield x
