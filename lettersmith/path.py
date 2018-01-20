from urllib.parse import urlparse
from pathlib import Path, PurePath
from os import sep, listdir, path, walk
import re
from fnmatch import fnmatch


_STRANGE_CHARS = "[](){}<>:^&%$#@!'\"|*~`,"
STRANGE_CHAR_PATTERN = "[{}]".format(re.escape(_STRANGE_CHARS))


def space_to_dash(text):
    return re.sub("\s+", "-", text)


def remove_strange_chars(text):
    return re.sub(STRANGE_CHAR_PATTERN, "", text)


def to_slug(text):
    """Given some text, return a nice URL"""
    text = str(text).strip().lower()
    text = remove_strange_chars(text)
    text = space_to_dash(text)
    return text


def to_title(pathlike):
    """
    Read a pathlike as a title. This takes the stem and removes any
    leading "_".
    """
    stem = PurePath(pathlike).stem
    return stem[1:] if stem.startswith("_") else stem


def is_file_like(pathlike):
    """Check if path is file-like, that is, ends with an `xxx.xxx`"""
    return len(PurePath(pathlike).suffix) > 0


def ensure_trailing_slash(pathlike):
    """Append a trailing slash to a path if missing."""
    path_str = str(pathlike)
    if is_file_like(path_str) or path_str.endswith("/"):
        return path_str
    else:
        return path_str + "/"


def is_local_url(url):
    """Does the URL have a scheme?"""
    o = urlparse(url)
    return not o.scheme


def qualify_url(pathlike, base="/"):
    path_str = str(pathlike)
    if not path_str.startswith(base) and is_local_url(path_str):
        return base + path_str
    else:
        return path_str


def remove_base_slash(any_path):
    """Remove base slash from a path"""
    return re.sub("^/", "", any_path)


def to_nice_path(ugly_pathlike):
    """
    Makes an ugly path into a "nice path". Nice paths are paths that end with
    an index file, so you can reference them `like/this/` instead of
    `like/This.html`.

    ugly_path:
        some/File.md

    nice_path:
        some/file/index.html
    """
    purepath = PurePath(ugly_pathlike)
    # Don't touch index pages
    if purepath.stem == "index":
        return purepath
    index_file = "index" + purepath.suffix
    index_path = PurePath(purepath.parent, purepath.stem, index_file)
    # Slug-ify and then convert slug string to path object.
    nice_path = PurePath(to_slug(index_path))
    return nice_path


def to_url(pathlike, base="/"):
    """
    Makes a nice path into a url.
    Basically gets rid of the trailing `index.html`.

    nice_path:
        some/file/index.html

    url:
        /some/file/
    """
    slug = to_slug(pathlike)
    purepath = PurePath(slug)
    if purepath.stem == "index":
        purepath = ensure_trailing_slash(purepath.parent)
    qualified = qualify_url(purepath, base=base)
    return qualified


def body(pathlike):
    """
    Return the "body" of the path...
    Everything except the top level directory.
    """
    body_parts = PurePath(pathlike).parts[1:]
    return PurePath(*body_parts)


def nice_name(a_path):
    """
    Get the "nice name" of a path... If the path ends with index.html,
    return the directory name above instead.
    """
    dirname, basename = path.split(a_path)
    if basename.endswith("index.html"):
        basename = path.basename(dirname)
    name, ext = path.splitext(basename)
    return name


def nice_dirname(nice_path):
    """
    Get the dirname of a "nice" path... If the path ends with index.html,
    return the directory name above instead.
    """
    dirname, basename = path.split(nice_path)
    if basename.endswith("index.html"):
        dirname = path.dirname(dirname)
    return dirname


def change_basename(file_path, new_basename):
    """
    Change the basename of a path, leaving the rest untouched.
    """
    basename = path.basename(file_path)
    return re.sub(basename + "$", new_basename, file_path, count=1)


def is_draft(pathlike):
    return PurePath(pathlike).name.startswith("_")


def is_dotfile(pathlike):
    return PurePath(pathlike).name.startswith(".")


def is_config_file(pathlike):
    """Check if the file is a lettersmith config file"""
    return PurePath(pathlike).name == "lettersmith.yaml"


def is_doc_file(pathlike):
    """
    Is this path a valid doc-like path?

    
    """
    return (is_file_like(pathlike)
        and not is_dotfile(pathlike)
        and not is_config_file(pathlike))


def is_index(pathlike):
    return PurePath(pathlike).stem == 'index'


def tld(pathlike):
    """
    Get the name of the top-level directory in this path.
    """
    parts = PurePath(pathlike).parts
    return parts[0] if len(parts) > 1 else ''


def read_dir(some_path):
    """
    Read a path to return the directory portion.
    If the path looks like a file, will return the dirname.
    Otherwise, will leave the path untouched.
    """
    return path.dirname(some_path) if is_file_like(some_path) else some_path


def is_child_dir(path_a, path_b):
    """
    What is a child dir?

        foo/bar/baz.html
        foo/bar/bing/bla.html # is_child_dir
    """
    return path.dirname(read_dir(path_b)) == read_dir(path_a)


def is_child_index(path_a, path_b):
    """
    What is a child index?

        foo/bar/baz.html
        foo/bar/bing/index.html # is_child_dir
    """
    return (
        is_index(path_b) and
        read_dir(path_a) == path.dirname(read_dir(path_b)))


def is_sibling(path_a, path_b):
    """
    What is a sibling:

    foo/bar/baz.html
    foo/bar/bing.html

    What is not a sibling:

    foo/bar/boing/index.html
    """
    return (
        path.dirname(path_a) == path.dirname(path_b)
        and not is_index(path_b))


def has_ext(pathlike, extensions):
    """
    Check to see if the extension of the pathlike matches any of the
    extensions in `extensions`.
    """
    return PurePath(pathlike).suffix in extensions


def glob_all(pathlike, globs):
    """
    Given a pathlike and an iterable of glob patterns, will glob
    all of them under the path.
    Returns a generator of all results.
    """
    realpath = Path(pathlike)
    for glob_pattern in globs:
        for p in realpath.glob(glob_pattern):
            yield p