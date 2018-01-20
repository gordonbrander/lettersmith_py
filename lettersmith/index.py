"""
Tools for indexing docs
"""

_EMPTY_TUPLE = tuple()

class Index:
    """
    A simple class for creating a mutable index.
    Each index key is deduped.
    """
    def index(self, key, value):
        try:
            if value not in self.__dict__[key]:
                self.__dict__[key].append(value) 
        except KeyError:
            self.__dict__[key] = [value]
        return self

    def index_many(self, key, values):
        for value in values:
            self.index(key, value)
        return self

    def __setitem__(self, key, value):
        self.index(key, value)

    def __getitem__(self, key):
        try:
            return tuple(self.__dict__[key])
        except KeyError:
            return _EMPTY_TUPLE

    def items(self):
        """
        Yield items, dictionary-style
        """
        return ((key, tuple(value)) for key, value in self.__dict__.items())

    def to_dict(self):
        """
        Get a copy of the current state of the index, as a dict.
        """
        return {key: value for key, value in self.items()}