"""
Tools for working with files.

Files are namedtuples that represent the raw bytes in a file to be
copied or transformed.
"""
from collections import namedtuple
from pathlib import PurePath
from lettersmith.date import read_file_times, EPOCH, to_datetime
from lettersmith import doc as Doc


File = namedtuple("File", (
    "id_path", "output_path", "input_path",
    "created", "modified", "blob"
))
File.__doc__ = """
Files are namedtuples that represent the raw bytes in a file to be
copied or transformed.

Files contain a `blob` field that contains the bytes of the file.
"""


def create(id_path, output_path, blob,
    input_path=None, created=EPOCH, modified=EPOCH):
    """
    Create a File tuple, populating it with sensible defaults
    """
    return File(
        id_path=str(id_path),
        output_path=str(output_path),
        input_path=str(input_path) if input_path is not None else None,
        created=to_datetime(created),
        modified=to_datetime(modified),
        blob=bytes(blob)
    )


def load(pathlike):
    """
    Loads a File namedtuple from a file path.
    `blob` field will contain bytes of file.
    Returns a File.
    """
    file_created, file_modified = read_file_times(pathlike)
    with open(pathlike, 'rb') as f:
        blob = f.read()
    return create(
        id_path=pathlike,
        output_path=pathlike,
        input_path=pathlike,
        created=file_created,
        modified=file_modified,
        blob=blob
    )


def writeable(file):
    """
    Return a writeable tuple for file.

    writeable tuple is any 2-tuple of `output_path`, `bytes`.
    `lettersmith.write` knows how to write these tuples to disk.
    """
    return file.output_path, file.blob


def to_doc(file):
    """
    Create a Doc from a File.
    """
    return Doc.create(
        id_path=file.id_path,
        output_path=file.output_path,
        input_path=file.input_path,
        created=file.created,
        modified=file.modified,
        content=file.blob.decode()
    )


def from_doc(file):
    """
    Create a File from a Doc.
    """
    return create(
        id_path=doc.id_path,
        output_path=doc.output_path,
        input_path=doc.input_path,
        created=doc.created,
        modified=doc.modified,
        blob=doc.content.encode()
    )