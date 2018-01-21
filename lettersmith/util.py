"""
Utility functions.
Mostly tools for working with dictionaries and iterables.
"""
from functools import reduce


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


def set(d, k, v):
    """
    Set or delete an attribute
    """
    if v != None:
        d[k] = v
    else:
        try:
            del d[k]
        except KeyError:
            pass
    return d


def merge(d, patch):
    """
    Merge 2 dictionaries, returning a new dictionary.
    `None` values in `patch` are treated as "delete this key".
    """
    out = d.copy()
    for key, value in patch.items():
        set(out, key, value)
    return out


def put(d, k, v):
    """
    Given a dict d, set value v at key k, returning new dict.
    New dict is a shallow copy of dict d.
    """
    return set(d.copy(), k, v)


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
    return (f(x, *args, **kwargs) for x in iterable if predicate(x))


def find(iterable, predicate, default=None):
    """Find first match to predicate, or return default"""
    return next((x for x in iterable if predicate(x)), default)


def pick(d, keys):
    """
    Return a copy of the object, filtered to only have values for the
    whitelisted array of valid keys.
    """
    return {k: v for k, v in d.items() if k in keys}


_EMPTY_TUPLE = tuple()


def has(x, key, value):
    """
    Check for a value in a deep object.
    `key` is a key path (can be a single key or an iterable of keys).
    """
    return get(x, key) == value


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


def where(iterable_of_dicts, key, value):
    """
    Query an iterable of dictionaries for keys matching value.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in iterable_of_dicts if has(x, key, value))


def where_not(iterable_of_dicts, key, value):
    """
    Query an iterable of dictionaries for keys NOT matching value.
    This may mean the key does not exist, or the value does not match.
    `key` may be an iterable of keys representing a key path.
    """
    return (x for x in iterable_of_dicts if not has(x, key, value))


def where_key(iterable_of_dicts, key):
    """
    Query an iterable of dictionaries
    """
    return (x for x in iterable_of_dicts if has_key(x, key))


def where_contains(iterable_of_dicts, key, value):
    """
    Query an iterable of dictionaries (optionally sorted)
    """
    return (x for x in iterable_of_dicts if contains(x, key, value))


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
