"""
Tools for working with Doc type.

Docs are namedtuples that represent a file to be transformed.
The `content` field of a doc contains the file contents, read as a
Python string with UTF-8 encoding.

Most lettersmith plugins transform Docs or iterables of Docs.

For working with non-text files, images, binary files, or text files
with other encodings, see `lettersmith.file` which stores the raw bytes
instead of reading them into a Python string.
"""
from pathlib import PurePath, Path
import json
from collections import namedtuple
from functools import wraps

import frontmatter
import yaml

from lettersmith.util import mix
from lettersmith.date import read_file_times, EPOCH, to_datetime
from lettersmith import path as pathtools
from lettersmith import lens
from lettersmith.lens import (
    Lens, lens_compose, get, put, key, over_with, update
)
from lettersmith.func import compose


Doc = namedtuple("Doc", (
    "id_path", "output_path", "input_path", "created", "modified",
    "title", "content", "meta", "template"
))
Doc.__doc__ = """
Docs are namedtuples that represent a document to be transformed,
and eventually written to disk.

Docs contain a content field. This is a string that typically contains the
contents of the file.
"""


def create(id_path, output_path,
    input_path=None, created=EPOCH, modified=EPOCH,
    title="", content="", meta=None, template=""):
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
        meta=meta if meta is not None else {},
        template=str(template)
    )


def load(pathlike):
    """
    Loads a doc namedtuple from a file path.
    `content` field will contain contents of file.
    Typically, you decorate the doc later with meta and other fields.

    Returns a doc.
    """
    file_created, file_modified = read_file_times(pathlike)
    with open(pathlike, 'r') as f:
        content = f.read()
    title = pathtools.to_title(pathlike)
    return create(
        id_path=pathlike,
        output_path=pathlike,
        input_path=pathlike,
        created=file_created,
        modified=file_modified,
        title=title,
        meta={},
        content=content
    )


def writeable(doc):
    """
    Return a writeable tuple for doc.

    writeable tuple is any 2-tuple of `output_path`, `bytes`.
    `lettersmith.write` knows how to write these tuples to disk.
    """
    return doc.output_path, doc.content.encode()


id_path = Lens(
    lambda doc: doc.id_path,
    lambda doc, id_path: doc._replace(id_path=id_path)
)


output_path = Lens(
    lambda doc: doc.output_path,
    lambda doc, output_path: doc._replace(output_path=output_path)
)

ext = lens_compose(output_path, pathtools.ext)

title = Lens(
    lambda doc: doc.title,
    lambda doc, title: doc._replace(title=title)
)


content = Lens(
    lambda doc: doc.content,
    lambda doc, content: doc._replace(content=content)
)


created = Lens(
    lambda doc: doc.created,
    lambda doc, created: doc._replace(created=created)
)


modified = Lens(
    lambda doc: doc.modified,
    lambda doc, modified: doc._replace(modified=modified)
)


meta = Lens(
    lambda doc: doc.meta,
    lambda doc, meta: doc._replace(meta=meta)
)


template = Lens(
    lambda doc: doc.template,
    lambda doc, template: doc._replace(template=template)
)


meta_summary = lens_compose(meta, key("summary", ""))


def update_meta(doc, patch):
    """
    Mix keys from `patch` into `doc.meta`.
    """
    return update(meta, mix, doc, patch)


def with_ext_html(doc):
    """
    Set doc extension to ".html"
    """
    return put(ext, doc, ".html")


output_tld = compose(pathtools.tld, output_path.get)
id_tld = compose(pathtools.tld, id_path.get)


_infer_template = compose(
    pathtools.ext_html,
    pathtools.to_slug,
    id_tld
)


def autotemplate(doc):
    """
    Set template based on top-level directory in doc's id_path.

    E.g. if top-level-directory is "posts", template gets set to "posts.html".
    """
    if get(template, doc) != "":
        return doc
    else:
        return put(template, doc, _infer_template(doc))


def with_template(t):
    """
    Set template `t`, but only if doc doesn't have one already.
    """
    def with_template_on_doc(doc):
        if get(template, doc) != "":
            return doc
        else:
            return put(template, doc, t)
    return with_template_on_doc


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
        "content": doc.content,
        "meta": doc.meta,
        "template": doc.template
    }


def uplift_meta(doc):
    """
    Reads "magic" fields in the meta and uplifts their values to doc
    properties.

    We use this to uplift...

    - title
    - created
    - modified
    - permalink
    - template

    ...in the frontmatter, overriding original or default values on doc.
    """
    return doc._replace(
        title=doc.meta.get("title", doc.title),
        created=to_datetime(doc.meta.get("created", doc.created)),
        modified=to_datetime(doc.meta.get("modified", doc.modified)),
        output_path=doc.meta.get("permalink", doc.output_path),
        template=doc.meta.get("template", "")
    )


class DocException(Exception):
    pass


def annotate_exceptions(func):
    """
    Decorates a mapping function for docs, giving it a more useful
    exception message.
    """
    @wraps(func)
    def func_with_annotated_exceptions(doc):
        try:
            return func(doc)
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
    return func_with_annotated_exceptions


@annotate_exceptions
def parse_frontmatter(doc):
    """
    Parse frontmatter as YAML. Set frontmatter on meta field, and
    remaining content on content field.

    If there is no frontmatter, will set an empty object on meta field,
    and leave content as-is.
    """
    meta, content = frontmatter.parse(doc.content)
    return doc._replace(
        meta=meta,
        content=content
    )


uplift_frontmatter = compose(uplift_meta, parse_frontmatter)


def renderer(render):
    """
    Create a renderer for doc content using a string rendering function.

    Will also annotate any exceptions that happen during rendering,
    transforming them into DocExceptions that will record the doc's
    id_path and the render function where exception occurred.

    Can be used as a decorator.
    """
    return annotate_exceptions(over_with(content, render))