from os import path
from pathlib import PurePath
import json

import frontmatter

from lettersmith.date import parse_iso_8601, read_file_times, EPOCH
from lettersmith.file import write_file_deep
from lettersmith import yamltools
from lettersmith.stringtools import truncate, strip_html
from lettersmith import path as pathtools
from lettersmith.util import put, merge, unset, pick


def load_raw(pathlike, relative_to=""):
    """
    Loads a basic doc dictionary from a file path. This dictionary
    contains content string, and some basic information about the file.
    Typically, you decorate the doc later with meta and other fields.

    Returns a dictionary.
    """
    file_created_time, file_modified_time = read_file_times(pathlike)
    with open(pathlike) as f:
        content = f.read()
        input_path = PurePath(pathlike)
        simple_path = input_path.relative_to(relative_to)
        output_path = pathtools.to_nice_path(simple_path)

        return {
            "file_created_time": file_created_time,
            "file_modified_time": file_modified_time,
            "input_path": str(input_path),
            "simple_path": str(simple_path),
            "output_path": str(output_path),
            "content": content
        }


def load(pathlike, relative_to=""):
    """
    Loads a doc dictionary with optional headmatter from a file path.
    This dictionary contains content string, meta from the headmatter,
    and some basic information about the file.

    Returns a dictionary.
    """
    return parse_doc_frontmatter(load_raw(pathlike, relative_to))


def load_yaml(pathlike, relative_to=""):
    """
    Loads a doc dictionary from a YAML file.
    This dictionary contains an empty content string, meta from the file,
    and some basic information about the file.

    Returns a dictionary.
    """
    return parse_doc_yaml(load_raw(pathlike, relative_to))


def load_json(pathlike, relative_to=""):
    """
    Loads a doc dictionary from a JSON file.
    This dictionary contains an empty content string, meta from the file,
    and some basic information about the file.

    Returns a dictionary.
    """
    return parse_doc_json(load_raw(pathlike, relative_to))


def parse_doc_frontmatter(doc):
    """
    Split headmatter from doc content. Sets headmatter meta as doc meta.
    Sets content as content.

    If no meta is present, sets an empty dict as meta.
    """
    meta, content = frontmatter.parse(doc["content"])
    return merge(doc, {
        "meta": meta,
        "content": content
    })


def parse_doc_yaml(doc):
    """
    Load doc content as YAML data
    """
    meta = yamltools.loads(doc["content"])
    return merge(doc, {
        "meta": meta,
        "content": ""
    })


def parse_doc_json(doc):
    """
    Load doc content as JSON data
    """
    meta = json.loads(doc["content"])
    return merge(doc, {
        "meta": meta,
        "content": ""
    })


def rm_content(doc):
    """
    Remove the content field.
    Useful if you need to collect a lot of docs into memory and the content
    field is huge. Pairs well with `reload_content`.

    Returns a new doc.
    """
    return unset(doc, ("content",))


def reload_content(doc):
    """
    Reload the content field, if missing.

    Returns a new doc.
    """
    if doc.get("content"):
        return doc
    else:
        try:
            with open(doc["input_path"]) as f:
                raw = f.read()
                meta, content = frontmatter.parse(raw)
                return put(doc, "content", content)
        except KeyError:
            return put(doc, "content", "")


def write(doc, output_dir):
    """
    Write a doc to the filesystem.

    Uses `doc["output_path"]` and `output_dir` to construct the output path.
    """
    write_file_deep(path.join(output_dir, doc["output_path"]), doc["content"])


def read_summary(doc, max_len=250, suffix="..."):
    """
    Read or generate a summary for a doc.
    Returns a string.
    """
    try:
        return doc["meta"]["summary"]
    except KeyError:
        return truncate(strip_html(doc.get("content", "")), max_len, suffix)


def read_title(doc):
    """
    Generate a title for the doc. Use either doc.meta.title, or
    derive a title from the filename.
    """
    try:
        return doc["meta"]["title"]
    except KeyError:
        return pathtools.to_title(doc["input_path"])


def read_date(doc):
    """
    Parse date from headmatter, or use file created time.
    """
    try:
        return parse_iso_8601(doc["meta"]["date"])
    except (ValueError, TypeError, KeyError):
        return doc.get("file_created_time", EPOCH)


def read_modified(doc):
    """
    Parse modified date from headmatter, or use file created time.
    """
    try:
        return parse_iso_8601(doc["meta"]["modified"])
    except (ValueError, TypeError, KeyError):
        return doc.get("file_modified_time", EPOCH)


def decorate_smart_items(doc):
    """
    Decorate doc with a variety of derived items, like automatic
    title, summary, etc.

    These are mostly computed properties that rely on logic or more than
    one value of the doc. Useful to have around in the template, where
    it's awkward to derive values with functions.
    """
    return merge(doc, {
        "title": read_title(doc),
        "section": pathtools.tld(doc["simple_path"]),
        "date": read_date(doc),
        "modified": read_modified(doc)
    })


def decorate_summary(doc):
    """
    Add a summary item to doc.
    """
    return put(doc, "summary", read_summary(doc))

# Whitelist of keys to keep for li objects
_LI_KEYS = (
    "title",
    "date",
    "modified",
    "file_created_time",
    "file_modified_time",
    "simple_path",
    "output_path",
    "section",
    "meta",
    "summary"
)


def to_li(doc):
    """
    Return a "list item" version of the doc... a small dictionary
    with a handful of whitelisted fields. This is typically what is
    used for indexes.
    """
    return pick(doc, _LI_KEYS)


def change_ext(doc, ext):
    """Change the extention on a doc's output_path, returning a new doc."""
    updated_path = PurePath(doc["output_path"]).with_suffix(ext)
    return put(doc, "output_path", updated_path)


def with_path(glob):
    """
    Check if a path matches glob pattern.
    """
    def has_path(doc):
        return fnmatch(doc["simple_path"], glob)
    return has_path