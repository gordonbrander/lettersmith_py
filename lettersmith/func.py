"""
Tools for working with higher-order functions.
"""
from functools import reduce, wraps


def id(x):
    """
    The id function.
    """
    return x


def _compose2(b, a):
    """Compose 2 functions"""
    def composed(x):
        """Composed function"""
        return b(a(x))
    return composed


def compose(*funcs):
    """Compose n functions from right to left"""
    return reduce(_compose2, funcs, id)


def thrush(*funcs):
    """
    Compose n functions from left to right.

    This is the same as compose, but using left-to-right application
    instead of right-to-left application.

    What's with the name?

    Following on Racket's naming convention
    https://docs.racket-lang.org/point-free/index.html

    It's named after
    https://en.wikipedia.org/wiki/To_Mock_a_Mockingbird
    """
    return reduce(_compose2, reversed(funcs), id)


def _apply_to(value, func):
    """
    Apply value to a single argument function.
    """
    return func(value)


def pipe(value, *funcs):
    """
    Pipe value through a series of single argument functions.
    This is basically a function version of a pipeline operator.

        pipe(value, a, b, c)

    is equivalent to

        c(b(a(value)))

    Returns transformed value.
    """
    return reduce(_apply_to, funcs, value)


def composable(func):
    """
    Decorator to transform a function into a composable function
    that consumes all of the "rest" of the arguments (everything
    after the first argument), then returns a bound function taking
    one argument (the first argument).
    """
    @wraps(func)
    def composable_func(*args, **kwargs):
        return rest(func, *args, **kwargs)
    return composable_func


def rest(func, *args, **kwargs):
    """
    Binds the "rest" of the arguments, then returns a bound
    function taking one argument (the first argument).
    """
    @wraps(func)
    def bound(first):
        return func(first, *args, **kwargs)
    return bound