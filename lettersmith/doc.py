from os import path
from pathlib import PurePath
import json
from datetime import datetime

import frontmatter

from lettersmith.date import parse_iso_8601, read_file_times, EPOCH
from lettersmith.file import write_file_deep
from lettersmith import yamltools
from lettersmith.stringtools import truncate, strip_html
from lettersmith import path as pathtools
from lettersmith.util import put, merge, pick
from lettersmith import stub as Stub


_EMPTY_TUPLE = tuple()


def doc(id_path, output_path,
    input_path=None, created_time=None, modified_time=None,
    title="", content="", section="", meta=None, templates=None):
    """
    Create a doc dict, populating it with sensible defaults

    Doc dictionaries contain a content string — typically the content of the
    file. Since this can take up quite a bit of memory, it's typical to avoid
    collecting docs into memory... we usually operate over generators that yield
    docs one-at-a-time.

    For cross-referencing things in-memory, we use Stubs. Stubs are meant to
    be stub docs. They contain just meta information about the doc.
    """
    return {
        "id_path": str(id_path),
        "output_path": str(output_path),
        "input_path": str(input_path) if input_path else None,
        "created_time":
            created_time if type(created_time) is datetime else datetime.now(),
        "modified_time":
            modified_time if type(modified_time) is datetime else datetime.now(),
        "title": str(title),
        "content": str(content),
        "section": str(section),
        "meta": meta if type(meta) is dict else {},
        "templates": templates if type(templates) is tuple else _EMPTY_TUPLE
    }


def load(pathlike, relative_to=""):
    """
    Loads a basic doc dictionary from a file path. This dictionary
    contains content string, and some basic information about the file.
    Typically, you decorate the doc later with meta and other fields.
    Create a doc dict, populating it with sensible defaults

    Returns a dictionary.
    """
    created_time, modified_time = read_file_times(pathlike)
    with open(pathlike) as f:
        meta, content = frontmatter.parse(f.read())
        input_path = PurePath(pathlike)
        id_path = input_path.relative_to(relative_to)
        output_path = pathtools.to_nice_path(id_path)
        section = pathtools.tld(id_path)
        title = meta.get("title", pathtools.to_title(input_path))
        return doc(
            id_path=id_path,
            output_path=output_path,
            input_path=input_path,
            created_time=created_time,
            modified_time=modified_time,
            title=title,
            section=section,
            meta=meta,
            content=content
        )


def to_stub(doc, max_len=250, suffix="..."):
    try:
        summary = doc["meta"]["summary"]
    except KeyError:
        summary = truncate(strip_html(doc["content"]), max_len, suffix)

    return Stub.stub(
        id_path=doc["id_path"],
        output_path=doc["output_path"],
        input_path=doc["input_path"],
        created_time=doc["created_time"],
        modified_time=doc["modified_time"],
        title=doc["title"],
        summary=summary,
        section=doc["section"],
        meta=doc["meta"]
    )


def write(doc, output_dir):
    """
    Write a doc to the filesystem.

    Uses `doc["output_path"]` and `output_dir` to construct the output path.
    """
    write_file_deep(path.join(output_dir, doc["output_path"]), doc["content"])


def put_meta(doc, key, value):
    """
    Put a value into a doc's meta dictionary.
    Returns a new doc.
    """
    return put(doc, "meta", put(doc["meta"], key, value))


def change_ext(doc, ext):
    """Change the extention on a doc's output_path, returning a new doc."""
    updated_path = PurePath(doc["output_path"]).with_suffix(ext)
    return put(doc, "output_path", str(updated_path))


def with_path(glob):
    """
    Check if a path matches glob pattern.
    """
    def has_path(doc):
        return fnmatch(doc["id_path"], glob)
    return has_path