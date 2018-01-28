"""
Utility functions.
Mostly tools for working with dictionaries and iterables.
"""
from functools import reduce
from fnmatch import fnmatch


def compose2(f, e):
    """Compose 2 functions"""
    return lambda x: f(e(x))


def compose(fn, *fns):
    """Compose n functions"""
    return reduce(compose2, fns, fn)


def _get_key(d, key):
    return d[key]


def get(d, keys, default=None):
    """
    Get a value in a dictionary, or get a deep value in
    nested dictionaries.

    If `keys` is a string, will do a regular `dict.get()`.
    If `keys` is an iterable of strings, will attempt to do a deep get.
    If the get fails, will return `default` value.
    """
    if type(keys) == str:
        return d.get(keys, default)
    try:
        return reduce(_get_key, keys, d)
    except (KeyError, TypeError):
        return default


def merge(d, patch):
    """
    Merge 2 dictionaries, returning a new dictionary.
    """
    e = d.copy()
    for k, v in patch.items():
        e[k] = v
    return e


def put(d, k, v):
    """
    Given a dict d, set value v at key k, returning new dict.
    New dict is a shallow copy of dict d.
    """
    e = d.copy()
    e[k] = v
    return e


def merge_deep(a, b):
    """
    Merge 2 dictionaries recursively, returning a new dictionary.
    Any dict field will be merged recursively. For all other fields, the
    right-hand field wins.
    """
    target = {}
    for d in (a, b):
        for k, v in d.items():
            if (isinstance(v, dict) and
                isinstance(target.get(k, None), dict)):
                target[k] = merge_deep(target[k], v)
            else:
                set(target, k, v)
    return target


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


def map_match(predicate, f, iterable, *args, **kwargs):
    """
    Map any items in iterable that match `predicate`. Any item that
    doesn't pass `predicate` test is untouched — it will still be
    yielded by the generator, but it won't be mapped.
    """
    for x in iterable:
        if predicate(x):
            yield f(x, *args, **kwargs)
        else:
            yield x


def find(iterable, predicate, default=None):
    """Find first match to predicate, or return default"""
    return next((x for x in iterable if predicate(x)), default)


def pick(d, keys):
    """
    Create a new dict with only only the items for keys in `keys`.
    Basically, whitelist certain keys in the dict.
    """
    return {k: v for k, v in d.items() if k in keys}


def unset(d, keys):
    """
    Remove specified keys from dict.
    Basically, blacklist certain keys in the original dict.
    """
    return {k: v for k, v in d.items() if k not in keys}


_EMPTY_TUPLE = tuple()


def contains(x, key, value):
    """
    Check for the inclusion of a value in an indexable in a deep object.
    `key` is a key path (can be a single key or an iterable of keys).
    """
    return value in get(x, key, _EMPTY_TUPLE)


def has_key(x, key):
    """
    Check for the presence of a key in a deep object.
    `key` is a key path (can be a single key or an iterable of keys).
    """
    return get(x, key) != None


def where(dicts, key, value):
    """
    Query an iterable of dictionaries for keys matching value.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in dicts if get(x, key) == value)


def where_not(dicts, key, value):
    """
    Query an iterable of dictionaries for keys NOT matching value.
    This may mean the key does not exist, or the value does not match.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in dicts if get(x, key) != value)


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


def where_matches(dicts, key, glob):
    """
    Query an iterable of dictionaries, matching the value against a
    Unix glob-style pattern.

    Returns an iterable of matching dictionaries.
    """
    return (x for x in dicts if fnmatch(get(x, key), glob))


def sort(iterable, key=None, reverse=None):
    """
    Sort an iterable, returning a new list.
    This is the same thing as list.sort, but instead of sorting in place,
    it accepts any iterable and returns a new list.
    """
    l = list(iterable)
    l.sort(key=key, reverse=reverse)
    return l


def sort_by(iter_of_dicts, key, reverse=False, default=None):
    """Sort an iterable of dicts via a key path"""
    fkey = lambda x: get(x, key, default=default)
    return sort(iter_of_dicts, key=fkey, reverse=reverse)
