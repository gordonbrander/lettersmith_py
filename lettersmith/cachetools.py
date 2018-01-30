import shelve


def _get_simple_path(doc):
    return doc["simple_path"]


def write_cache(file_path, iterable, key=_get_simple_path):
    """
    Write an iterable of things to a shelf.
    Eacy value is indexed using the `key` function. By default
    this is configured to index doc objects.
    """
    with shelve.open(str(file_path)) as db:
        for value in iterable:
            db[key(value)] = value
            db.sync()


def read_cache(file_path):
    """
    Read an iterable of items from the cache.
    """
    with shelve.open(str(file_path)) as db:
        for k in db:
            yield db[k]