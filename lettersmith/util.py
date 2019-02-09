"""
Utility functions.
Mostly tools for working with dictionaries and iterables.
"""
from functools import reduce, singledispatch, wraps, partial
from fnmatch import fnmatch


def id(x):
    """
    The id function.
    """
    return x


def compose2(fb, fa):
    """Compose 2 functions"""
    return lambda x: fb(fa(x))


def compose(fa, *fn):
    """Compose n functions"""
    return reduce(compose2, fn, fa)


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


def matches_id_path(doc, glob):
    """
    Predicate function that tests whether the id_path of a thing
    (as determined by `get`) matches a glob pattern.
    """
    # We fast-path for "everything" matches.
    return fnmatch(get(doc, "id_path"), glob) if glob != "*" else True


def matching_id_path(glob):
    return lambda doc: matches_id_path(doc, glob)


def filter_id_path(docs, glob):
    return filter(matching_id_path(glob), docs)


def maps_if(predicate):
    """
    Decorate a function so that it only touches value if value
    passes predicate test.
    """
    def wrap(func):
        @wraps(func)
        def wrapped(x, *args, **kwargs):
            if predicate(x):
                return func(x, *args, **kwargs)
            else:
                return x
        return wrapped
    return wrap


def any_in(collection, values):
    """
    Check if any of a collection of values is in `collection`.
    Returns boolean.
    """
    for value in values:
        if value in collection:
            return True
    return False


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


def select(dicts, *keys):
    for d in dicts:
        yield tuple(get_deep(d, key) for key in keys)


def _compare_where(compare):
    """
    Query an iterable of dictionaries for keys matching value.
    `key` may be an iterable of keys representing a key path.
    """
    @wraps(compare)
    def where(dicts, key, value):
        for x in dicts:
            if compare(get_deep(x, key), value):
                yield x
    return where


@_compare_where
def where(a, b):
    return a == b


@_compare_where
def where_not(a, b):
    return a != b


@_compare_where
def where_gt(a, b):
    return a > b


@_compare_where
def where_lt(a, b):
    return a < b


@_compare_where
def where_len(a, b):
    return len(a) == b


@_compare_where
def where_len_gt(a, b):
    return len(a) > b


@_compare_where
def where_len_lt(a, b):
    return len(a) < b


@_compare_where
def where_in(a, b):
    try:
        return b in a
    except TypeError:
        return False


@_compare_where
def where_not_in(a, b):
    try:
        return b not in a
    except TypeError:
        return True


@_compare_where
def where_any_in(a, b):
    try:
        return any_in(a, b)
    except TypeError:
        return False


@_compare_where
def where_matches(value, glob):
    return fnmatch(value, glob)


def lift_iter(f):
    """
    Lift a function to consume an iterator instead of single values.
    """
    def f_iter(iter, *args, **kwargs):
        return (f(x, *args, **kwargs) for x in iter)
    return f_iter


def sort_by(dicts_iter, key, default=None, reverse=False):
    """Sort an iterable of dicts via a key path"""
    fkey = lambda x: get_deep(x, key, default=default)
    return sorted(dicts_iter, key=fkey, reverse=reverse)


def sort_by_len(dicts_iter, key, reverse=False):
    """Sort an iterable of dicts via a key path"""
    fkey = lambda x: len(get_deep(x, key, default=_EMPTY_TUPLE))
    return sorted(dicts_iter, key=fkey, reverse=reverse)


def sort_by_keys(dicts_iter, keys, defaults=_EMPTY_TUPLE, reverse=False):
    """
    Sort an iterable of dicts by multiple key values at once.
    `keys` is an iterable of keys that describe, in order, which values
    to sort by. Each key may be a key or a key path.
    `defaults` is an iterable of values that are used as defaults when
    a key is missing. It must be the same length as `keys`.

    This can be used to sort dicts by multiple fields, for example, by
    weight, as well as date.
    """
    dicts_tuple = tuple(dicts_iter)
    keys_tuple = tuple(keys)
    defaults_tuple = tuple(defaults)
    if (len(defaults_tuple) is not len(keys_tuple)):
        raise ValueError("defaults iterable must be same length as keys")
    fkey = lambda d: tuple(
        get_deep(d, key, default)
        for key, default in zip(keys_tuple, defaults_tuple)
    )
    return sorted(dicts_tuple, key=fkey, reverse=reverse)


def _first(pair):
    return pair[0]


def sort_items_by_key(dict, reverse=False):
    """
    Sort a dict's items by key, returning a sorted iterable of tuples.
    """
    return sorted(
        dict.items(),
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


def expand(f, iter):
    """
    Expand each item in `iter` using function `f`.
    `f` is expected to return an iterator itself... it "expands"
    each item.
    """
    for x in iter:
        for y in f(x)
            yield y