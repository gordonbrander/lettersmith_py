from pathlib import PurePath
import shutil
from lettersmith import doc as Doc
from lettersmith import file as File
from lettersmith.io import write_file_deep


def writer(writeable):
    """
    Lift a `writeable` function that reads a data object and returns
    a 2-tuple of `(pathlike, bytes)`.

    Returns a `write` function that knows how to take these 2-tuples
    and write them to disk.
    """
    def write(things, directory):
        """
        Write files to `directory`.
        """
        dir_path = PurePath(directory)
        shutil.rmtree(dir_path, ignore_errors=True)
        written = 0
        for thing in things:
            written = written + 1
            output_path, blob = writeable(thing)
            write_file_deep(
                dir_path.joinpath(output_path),
                blob,
                mode="wb"
            )
        return {"written": written}
    return write


def writeable(thing):
    """
    Write a doc or file to `output_path`.
    """
    if isinstance(thing, Doc.Doc):
        return Doc.writeable(thing)
    elif isinstance(thing, File.File):
        return File.writeable(thing)
    else:
        msg = (
            "Don't know how to convert {type} to (path, bytes). "
            "If you are using a custom document type, you can create "
            "your own function that knows how to return (path, bytes). "
            "Then you can pass that function to writer() to create "
            "a custom write function."
        )
        raise ValueError(msg.format(type=type(thing)))


write = writer(writeable)