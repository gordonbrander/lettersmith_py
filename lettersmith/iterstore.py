from lettersmith import jsontools


class IterStore:
    """
    Consume an iterable, serializing it and saving it to disk.
    You can read the stored iter back out via the `__iter__` method.
    This allows you to use it as an iterator that may be consumed
    multiple times from disk.
    """
    def __init__(self, iterable, file_path):
        self.file_path = file_path
        jsontools.write_chunks(iterable, file_path)

    def __iter__(self):
        return jsontools.load_chunks(self.file_path)


def store(iterable, file_path):
    """
    Store the iterator at `file_path`.

    Right now this is just a proxy for IterStore initialization.
    """
    return IterStore(iterable, file_path)