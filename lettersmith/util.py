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
def get(d, key, default=None):
    """
    A singledispatch getter function.
    """
    return getattr(d, key, default)


@get.register(dict)
def get_dict(d, key, default=None):
    """
    Getter for dictionaries. Does a get on dictionary items.
    """
    return d.get(key, default)


def get_deep(d, keys, default=None):
    """
    Get a value in a dictionary, or get a deep value in
    nested dictionaries.

    If `keys` is a string, will do a regular `dict.get()`.
    If `keys` is an iterable of strings, will attempt to do a deep get.
    If the get fails, will return `default` value.
    """
    if type(keys) is str:
        return get(d, keys)
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


def match_mapper(predicate):
    """
    This decorator lifts a fuction which operates on a single item
    to one that operates over an iterable of items.

    Items that match `predicate` are mapped with `f`. Items which
    do not are still yielded, but not touched.

    The resulting function returns a generator for results.
    """
    def decorate(f):
        def map_match(iterable, *args, **kwargs):
            for x in iterable:
                if predicate(x):
                    yield f(x, *args, **kwargs)
                else:
                    yield x
        return map_match
    return decorate


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


def decorate_match_by_group(f, *args, **default_kwargs):
    """
    Decorates a function `f` with an additional `match` keyword argument.
    This argument is a Unix-style glob string that will be used to
    filter matches.

    This is meant to be used to decorate functions that take an iterable
    and return an iterable.
    """
    def f_wrap(docs, groups):
        for glob, group_kwargs in groups.items():
            matches = match_by_id_path(docs, glob)
            # Allow group_kwargs to overshadow default_kwargs.
            kwargs = merge(default_kwargs, group_kwargs)
            yield f(matches, *args, **kwargs)
    return f_wrap


_EMPTY_TUPLE = tuple()


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
    return (x for x in dicts if fnmatch(get_deep(x, key), glob))


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
