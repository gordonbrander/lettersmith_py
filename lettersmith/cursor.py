"""
Utilities for creating views on datastructures. Lens-like things.
"""

def extra_reader(read):
    """
    Given a getter function, returns a decorator for functions that will
    read the "extra" args passed to that function.
    """
    def wrap(func):
        def wrapped(x, *args, **kwargs):
            rargs = read(*args, **kwargs)
            return func(x, **rargs)
        return wrapped
    return wrap
