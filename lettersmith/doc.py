from os import path
from pathlib import PurePath
from datetime import date as Date

import frontmatter

from lettersmith.date import (parse_iso_8601, read_file_times)
from lettersmith.file import write_file_deep
from lettersmith.stringtools import truncate, strip_html
from lettersmith import path as pathtools
from lettersmith.util import put, merge


def load(pathlike):
    """
    Load doc from file path
    """
    file_created_time, file_modified_time = read_file_times(pathlike)
    with open(pathlike) as f:
        raw = f.read()
        meta, content = frontmatter.parse(raw)
        input_path = PurePath(pathlike)
        simple_path = pathtools.body(input_path)
        output_path = pathtools.to_nice_path(simple_path)
        # Use either the meta title or the file name as the title.
        try:
            title = meta["title"]
        except KeyError:
            title = pathtools.to_title(input_path)

        # Parse date from headmatter, or use file created time.
        try:
            date = parse_iso_8601(meta["date"])
        except (ValueError, TypeError, KeyError):
            date = file_created_time

        # Parse modified date from headmatter, or use file modified time.
        try:
            modified = parse_iso_8601(meta["modified"])
        except (ValueError, TypeError, KeyError):
            modified = file_modified_time

        return {
            "date": date,
            "modified": modified,
            "file_created_time": file_created_time,
            "file_modified_time": file_modified_time,
            "input_path": str(input_path),
            "simple_path": str(simple_path),
            "output_path": str(output_path),
            "section": pathtools.tld(simple_path),
            "title": title,
            "meta": meta,
            "content": content
        }


def rm_content(doc):
    """
    Remove the content field.
    Useful if you need to collect a lot of docs into memory and the content
    field is huge.

    Pairs well with `reload_content`.
    """
    return put(doc, "content", None)


def reload_content(doc):
    """
    Reload the content field, if missing.
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
    """Write a doc to filepath"""
    write_file_deep(path.join(output_dir, doc["output_path"]), doc["content"])


def summary(doc, max_len=250, suffix="..."):
    """Read or generate a summary for a doc"""
    try:
        return doc["meta"]["summary"]
    except KeyError:
        return truncate(strip_html(doc.get("content", "")), max_len, suffix)


def to_li(doc):
    return {
        "title": doc["title"],
        "date": doc["date"],
        "modified": doc["modified"],
        "file_modified_time": doc["file_modified_time"],
        "file_created_time": doc["file_created_time"],
        "input_path": doc.get("input_path"),
        "simple_path": doc["simple_path"],
        "output_path": doc["output_path"],
        "section": doc["section"],
        "taxonomy": doc.get("taxonomy", {}),
        "meta": doc.get("meta", {}),
        "summary": summary(doc)
    }


def change_ext(doc, ext):
    """Change the extention on a doc's output_path, returning a new doc"""
    updated_path = PurePath(doc["output_path"]).with_suffix(ext)
    return put(doc, "output_path", updated_path)


def with_path(glob):
    """
    Check if a path matches glob pattern
    """
    def has_path(doc):
        return fnmatch(doc["simple_path"], glob)
    return has_path