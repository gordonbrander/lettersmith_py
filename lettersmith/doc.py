from pathlib import PurePath, Path
import json
from collections import namedtuple
from functools import wraps

import frontmatter
import yaml

from lettersmith.date import read_file_times, EPOCH, to_datetime
from lettersmith.file import write_file_deep
from lettersmith import path as pathtools
from lettersmith.html import strip_html
from lettersmith.stringtools import first_sentence
from lettersmith.util import replace, get

Doc = namedtuple("Doc", (
    "id_path", "output_path", "input_path", "created", "modified",
    "title", "content", "section", "meta", "templates"
))
Doc.__doc__ = """
Docs are namedtuples that represent a document to be transformed,
and eventually written to disk.

Docs contain a content field. This is a string that typically contains the
contents of the file.
"""


def doc(id_path, output_path,
    input_path=None, created=EPOCH, modified=EPOCH,
    title="", content="", section="", meta=None, templates=None):
    """
    Create a Doc tuple, populating it with sensible defaults
    """
    return Doc(
        id_path=str(id_path),
        output_path=str(output_path),
        input_path=str(input_path) if input_path is not None else None,
        created=to_datetime(created),
        modified=to_datetime(modified),
        title=str(title),
        content=str(content),
        section=str(section),
        meta=meta if meta is not None else {},
        templates=templates if templates is not None else tuple()
    )


@get.register(Doc)
def get_doc(doc, key, default=None):
    return getattr(doc, key, default)


@replace.register(Doc)
def replace_doc(doc, **kwargs):
    """
    Replace items in a Doc, returning a new Doc.
    """
    return doc._replace(**kwargs)


def replace_meta(doc, **kwargs):
    """
    Put a value into a doc's meta dictionary.
    Returns a new doc.
    """
    return doc._replace(meta={**doc.meta, **kwargs})


def load(pathlike, relative_to=""):
    """
    Loads a basic doc dictionary from a file path.
    `content` field will contain contents of file.
    Typically, you decorate the doc later with meta and other fields.

    Returns a doc.
    """
    file_created, file_modified = read_file_times(pathlike)
    with open(pathlike, 'r') as f:
        content = f.read()
    input_path = PurePath(pathlike)
    id_path = input_path.relative_to(relative_to)
    section = pathtools.tld(id_path)
    title = pathtools.to_title(input_path)
    return doc(
        id_path=id_path,
        output_path=id_path,
        input_path=input_path,
        created=file_created,
        modified=file_modified,
        title=title,
        section=section,
        meta={},
        content=content
    )


def to_json(doc):
    """
    Serialize a doc as JSON-serializable data
    """
    return {
        "@type": "doc",
        "id_path": doc.id_path,
        "output_path": doc.output_path,
        "input_path": doc.input_path,
        "created": doc.created.timestamp(),
        "modified": doc.modified.timestamp(),
        "title": doc.title,
        "section": doc.section,
        "content": doc.content,
        # TODO manually serialize meta?
        "meta": doc.meta,
        "templates": doc.templates
    }


def write(doc, output_dir):
    """
    Write a doc to the filesystem.

    Uses `doc.output_path` and `output_dir` to construct the output path.
    """
    write_file_deep(PurePath(output_dir).joinpath(doc.output_path), doc.content)


def uplift_meta(doc):
    """
    Reads "magic" fields in the meta and uplifts their values to doc
    properties.

    We use this to uplift title, created, modified fields in the
    frontmatterm, overriding original or default values on doc.
    """
    return doc._replace(
        title=doc.meta.get("title", doc.title),
        created=to_datetime(doc.meta.get("created", doc.created)),
        modified=to_datetime(doc.meta.get("modified", doc.modified))
    )


def has_ext(doc, *exts):
    """
    Check if a doc has an extension.
    """
    return pathtools.has_ext(doc.id_path, *exts)


def with_ext(doc, ext):
    """Change the extention on a doc's output_path, returning a new doc."""
    updated_path = PurePath(doc.output_path).with_suffix(ext)
    return doc._replace(output_path=str(updated_path))


def get_summary(doc):
    """
    Get summary for doc. Uses "summary" meta field if it exists.
    Otherwise, generates a summary by truncating doc content.
    """
    try:
        return strip_html(doc.meta["summary"])
    except KeyError:
        return first_sentence(strip_html(doc.content))


class DocException(Exception):
    pass


def annotates_exceptions(func):
    """
    Decorates a mapping function for docs, giving it a more useful
    exception message.
    """
    @wraps(func)
    def map_doc(doc, *args, **kwargs):
        try:
            return func(doc, *args, **kwargs)
        except Exception as e:
            msg = (
                'Error encountered while mapping doc '
                '"{id_path}" with {module}.{func}.'
            ).format(
                id_path=doc.id_path,
                func=func.__qualname__,
                module=func.__module__
            )
            raise DocException(msg) from e
    return map_doc


@annotates_exceptions
def parse_frontmatter(doc):
    meta, content = frontmatter.parse(doc.content)
    return doc._replace(
        meta=meta,
        content=content
    )


def uplift_frontmatter(doc):
    """
    Parse frontmatter and uplift meta to meta fields.
    """
    return uplift_meta(parse_frontmatter(doc))