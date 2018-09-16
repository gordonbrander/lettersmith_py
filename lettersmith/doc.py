from pathlib import PurePath
import json
import hashlib
from collections import namedtuple
import pickle

import frontmatter
import yaml

from lettersmith.date import read_file_times, EPOCH, to_datetime
from lettersmith.file import write_file_deep
from lettersmith import path as pathtools
from lettersmith.util import replace, get, bind_extra, multidispatch


_EMPTY_TUPLE = tuple()

Doc = namedtuple("Doc", (
    "id_path", "output_path", "input_path", "created", "modified",
    "title", "content", "section", "meta", "templates"
))
Doc.__doc__ = """
Docs are namedtuples that represent a document to be transformed,
and eventually written to disk.

Docs contain a content field — usually the whole contents of a
file. Since this can take up quite a bit of memory, it's typical to avoid
collecting all docs into memory. We usually load and transform them in
generator functions so that only one is in memory at a time.

For collecting many in memory, and cross-referencing, we use Stubs.
Stubs are meant to be stub docs. They contain just meta information
about the doc. You can turn a doc into a stub with
`lettersmith.stub.from_doc(doc)`.
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
        templates=templates if templates is not None else _EMPTY_TUPLE
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


@bind_extra
def replace_meta(doc, **kwargs):
    """
    Put a value into a doc's meta dictionary.
    Returns a new doc.
    """
    return replace(doc, meta=replace(doc.meta, **kwargs))


class DocParseError(Exception):
    pass


# Export parsers to use with load.
parse_frontmatter = frontmatter.parse


def parse_yaml(s):
    """
    Parse a YAML string to meta and content.
    YAML is treated as meta. Content is empty string.
    """
    return yaml.load(s), ""


def parse_json(s):
    """
    Parse a YAML string to meta and content.
    YAML is treated as meta. Content is empty string.
    """
    return json.loads(s), ""


def load_and_parse(pathlike, parse=parse_frontmatter, relative_to=""):
    """
    Loads a basic doc dictionary from a file path. This dictionary
    contains content string, and some basic information about the file.
    Typically, you decorate the doc later with meta and other fields.
    Create a doc dict, populating it with sensible defaults

    parse is a function that takes a string, and returns a tuple of
    `(meta, content)`, where `meta` is a dictionary and `content` is a string.

    Returns a dictionary.
    """
    file_created, file_modified = read_file_times(pathlike)
    with open(pathlike, 'r') as f:
        try:
            meta, content = parse(f.read())
        # Raise a more useful exception that includes the doc's path.
        except Exception as e:
            msg = (
                'Error encountered while parsing '
                '"{path}" with {module}.{func}.'
            ).format(
                path=pathlike,
                func=parse.__qualname__,
                module=parse.__module__
            )
            raise DocParseError(msg) from e
    input_path = PurePath(pathlike)
    id_path = input_path.relative_to(relative_to)
    output_path = pathtools.to_nice_path(id_path)
    section = pathtools.tld(id_path)
    title = meta.get("title", pathtools.to_title(input_path))
    created = meta.get("created", file_created)
    modified = meta.get("modified", file_modified)
    return doc(
        id_path=id_path,
        output_path=output_path,
        input_path=input_path,
        created=created,
        modified=modified,
        title=title,
        section=section,
        meta=meta,
        content=content
    )


def _dispatch_by_ext(pathlike, relative_to):
    """
    Dispatch by the file extension of `pathlike`.
    """
    return PurePath(pathlike).suffix


@multidispatch(_dispatch_by_ext)
def load(pathlike, relative_to=""):
    """
    Load a file at `pathlike`, and parse it into a doc.

    By default, treats any file as a text file, and will parse YAML
    headmatter, placing the parsed result in the `meta` field of the doc.

    There are also special handlers registered for YAML and JSON files.
    These parse the file contents, place everything in meta, and
    assign an empty string to the content field.

    `load` is a multidispatch method, that dispatches on file extension,
    so you can also register your own handlers for other file extensions.
    Use decorator `@load.register(".someext")`.
    """
    return load_and_parse(pathlike, parse_frontmatter, relative_to)


@load.register(".yaml")
@load.register(".yml")
def load_yaml(pathlike, relative_to=""):
    """
    Load and parse a YAML file to a doc.

    Parses the file contents, places everything in meta, and
    assign an empty string to the content field.
    """
    return load_and_parse(pathlike, parse_yaml, relative_to)


@load.register(".json")
def load_json(pathlike, relative_to=""):
    """
    Load and parse a JSON file to a doc.

    Parses the file contents, places everything in meta, and
    assign an empty string to the content field.
    """
    return load_and_parse(pathlike, parse_json, relative_to)


def from_stub(stub):
    """
    Create a doc dictionary from an stub dictionary.
    This doc dictionary will have an empty "content" field.

    If you want to load a doc from a file stub with an `input_path`,
    use `load_doc` instead.
    """
    return doc(
        id_path=stub.id_path,
        output_path=stub.output_path,
        input_path=stub.input_path,
        created=stub.created,
        modified=stub.modified,
        title=stub.title,
        section=stub.section,
        meta=stub.meta
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


def _hashstr(s):
    return hashlib.md5(str(s).encode()).hexdigest()


def _cache_path(id_path):
    """
    Read a doc ID path
    """
    return PurePath(_hashstr(id_path)).with_suffix('.pkl')


def dump_cache(cache_path, doc):
    doc_cache_path = _cache_path(doc.id_path)
    with open(PurePath(cache_path, doc_cache_path), "wb") as f:
        pickle.dump(doc, f)
        return doc


def load_cache(cache_path, stub):
    doc_cache_path = _cache_path(stub.id_path)
    with open(PurePath(cache_path, doc_cache_path), "rb") as f:
        return pickle.load(f)


class Cache:
    """
    Memoized cache dump/load for docs
    """
    def __init__(self, cache_path):
        self.cache_path = PurePath(cache_path)

    def dump(self, doc):
        return dump_cache(self.cache_path, doc)

    def load(self, stub):
        return load_cache(self.cache_path, stub)


@bind_extra
def change_ext(doc, ext):
    """Change the extention on a doc's output_path, returning a new doc."""
    updated_path = PurePath(doc.output_path).with_suffix(ext)
    return replace(doc, output_path=str(updated_path))