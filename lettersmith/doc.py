from pathlib import PurePath, Path
import json
from collections import namedtuple
from functools import wraps

import frontmatter
import yaml

from lettersmith.util import mix
from lettersmith.date import read_file_times, EPOCH, to_datetime
from lettersmith.file import write_file_deep
from lettersmith import path as pathtools
from lettersmith import lens
from lettersmith.lens import Lens
from lettersmith.func import compose


Doc = namedtuple("Doc", (
    "id_path", "output_path", "input_path", "created", "modified",
    "title", "content", "section", "meta", "template"
))
Doc.__doc__ = """
Docs are namedtuples that represent a document to be transformed,
and eventually written to disk.

Docs contain a content field. This is a string that typically contains the
contents of the file.
"""


def doc(id_path, output_path,
    input_path=None, created=EPOCH, modified=EPOCH,
    title="", content="", section="", meta=None, template=""):
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
        template=str(template)
    )


def load(pathlike):
    """
    Loads a basic doc dictionary from a file path.
    `content` field will contain contents of file.
    Typically, you decorate the doc later with meta and other fields.

    Returns a doc.
    """
    file_created, file_modified = read_file_times(pathlike)
    with open(pathlike, 'r') as f:
        content = f.read()
    section = pathtools.tld(pathlike)
    title = pathtools.to_title(pathlike)
    return doc(
        id_path=pathlike,
        output_path=pathlike,
        input_path=pathlike,
        created=file_created,
        modified=file_modified,
        title=title,
        section=section,
        meta={},
        content=content
    )


id_path = Lens(
    lambda doc: doc.id_path,
    lambda doc, id_path: doc._replace(id_path=id_path)
)


output_path = Lens(
    lambda doc: doc.output_path,
    lambda doc, output_path: doc._replace(output_path=output_path)
)

title = Lens(
    lambda doc: doc.title,
    lambda doc, title: doc._replace(title=title)
)


content = Lens(
    lambda doc: doc.content,
    lambda doc, content: doc._replace(content=content)
)


section = Lens(
    lambda doc: doc.section,
    lambda doc, section: doc._replace(section=section)
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


meta_summary = lens.compose(meta, lens.key("summary", ""))


def update_meta(doc, patch):
    """
    Mix keys from `patch` into `doc.meta`.
    """
    return lens.update(meta, mix, doc, patch)


_as_file_name_html = compose(pathtools.ext_html, pathtools.to_slug)


def autotemplate(doc):
    """
    Set template based on doc section name.

    E.g. if section is "posts", template gets set to "posts.html".
    """
    if lens.get(template, doc) != "":
        return doc
    else:
        return lens.put(
            template,
            doc,
            _as_file_name_html(lens.get(section, doc))
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
        "meta": doc.meta,
        "template": doc.template
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
    meta, content = frontmatter.parse(doc.content)
    return doc._replace(
        meta=meta,
        content=content
    )


uplift_frontmatter = compose(uplift_meta, parse_frontmatter)