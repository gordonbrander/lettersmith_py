"""
A minimal implementation of Haskel-style lenses, inspired by Elm
Focus library.

Lenses let you create getters and setters for a complex data structure.
The combination of a getter and setter is called a lens.

Lenses can be composed to provide a way to do deep reads and deep writes
to complex data structures.    
"""
from collections import namedtuple
from functools import reduce


Lens = namedtuple("Lens", ("get", "put"))
Lens.__doc__ = """
Container type for Lenses. A lens is anything with a `get` and `put` method.
"""


def compose2(big_lens, small_lens):
    """
    Compose 2 lenses. This allows you to create a lens that can
    do a deep get/set.
    """
    def get(big):
        """
        Lens `get` method (composed)
        """
        return small_lens.get(big_lens.get(big))

    def put(big, small):
        """
        Lens `update` method (composed)
        """
        return big_lens.put(
            big,
            small_lens.put(big_lens.get(big), small)
        )

    return Lens(get, put)


def compose(big_lens, *smaller_lenses):
    """
    Compose many lenses
    """
    return reduce(compose2, smaller_lenses, big_lens)


def get(lens, big):
    """
    Get a value from `big` using `lens`.
    """
    return lens.get(big)


def put(lens, big, small):
    """
    Set a value in `big`.
    """
    return lens.put(big, small)


def over(lens, mapping, big):
    """
    Map value(s) in `big` using a `mapping` function.
    """
    return put(lens, big, mapping(get(lens, big)))


def key(k, default=None):
    """
    Lens to get and set a key on a dictionary, with default value.
    Because it allows for a default, it technically violates the
    lens laws. However, in practice, it's too darn useful not to have.
    """
    def get(big):
        """
        Get key from dict
        """
        return big.get(k, default)

    def put(big, small):
        """
        Put value in key from dict, returning new dict.
        """
        # Check that we're actually making a change before creating
        # a new dict.
        if big.get(k, default) == small:
            return big
        else:
            return {**big, k: small}

    return Lens(get, put)


def pick(d, keys):
    return {k: d[k] for k in keys}


def keys(*keys):
    """
    Lens to get and set a key on a dictionary, with default value.
    """
    def get(big):
        """
        Get key from dict
        """
        return pick(big, keys)

    def put(big, small):
        """
        Put value in key from dict, returning new dict.
        """
        patch = pick(small, keys)
        return {**big, **patch}

    return Lens(get, put)
