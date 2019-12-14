"""
A minimal implementation of Haskel-style lenses

Inspired by Elm's Focus library and Racket's Lenses library.

Lenses let you create getters and setters for complex data structures.
The combination of a getter and setter is called a lens.

Lenses can be composed to provide a way to do deep reads and deep writes
to complex data structures.
"""
from collections import namedtuple
from functools import reduce


Lens = namedtuple("Lens", ("get", "put"))
Lens.__doc__ = """
Container type for Lenses.
A lens is any structure with `get` and `put` functions that
follow the lens signature.
"""


def _lens_compose2(big_lens, small_lens):
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


def lens_compose(big_lens, *smaller_lenses):
    """
    Compose many lenses
    """
    return reduce(_lens_compose2, smaller_lenses, big_lens)


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


def over(lens, func, big):
    """
    Map value(s) in `big` using a `mapping` function.
    """
    return put(lens, big, func(get(lens, big)))


def over_with(lens, func):
    """
    Given a lens and a function, returns a single-argument function
    that will map over value in `big` using `func`, and returning
    a new instance of `big`.
    """
    def over_bound(big):
        """
        Map value(s) in `big` using a bound mapping function.
        """
        return over(lens, func, big)
    return over_bound


def update(lens, up, big, msg):
    """
    Update `big` through an update function, `up` which takes the
    current small, and a `msg`, and returns a new small.
    """
    return put(lens, big, up(get(lens, big), msg))


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


def _pick(d, keys):
    return {k: d[k] for k in keys}


def keys(*keys):
    """
    Lens to get and set multiple keys on a dictionary. Note that
    no default values are allowed.
    """
    def get(big):
        """
        Get key from dict
        """
        return _pick(big, keys)

    def put(big, small):
        """
        Put value in key from dict, returning new dict.
        """
        patch = _pick(small, keys)
        return {**big, **patch}

    return Lens(get, put)