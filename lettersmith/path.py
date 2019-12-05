from urllib.parse import urlparse, urljoin
from pathlib import Path, PurePath
import re
from lettersmith.func import compose
from lettersmith.lens import Lens, put
from lettersmith import query


_STRANGE_CHARS = "[](){}<>:^&%$#@!'\"|*~`,"
_STRANGE_CHAR_PATTERN = "[{}]".format(re.escape(_STRANGE_CHARS))


def _space_to_dash(text):
    """Replace spaces with dashes."""
    return re.sub(r"\s+", "-", text)


def _remove_strange_chars(text):
    """Remove funky characters that don't belong in a URL."""
    return re.sub(_STRANGE_CHAR_PATTERN, "", text)


def _lower(s):
    return s.lower()


def _strip(s):
    return s.strip()


to_slug = compose(
    _space_to_dash,
    _remove_strange_chars,
    _lower,
    _strip,
    str
)


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
    """
    Qualify a URL with a basepath. Will leave URL if the URL is already
    qualified.
    """
    path_str = str(pathlike)
    if not path_str.startswith(base) and is_local_url(path_str):
        return urljoin(base, path_str)
    else:
        return path_str


def remove_base_slash(any_path):
    """Remove base slash from a path."""
    return re.sub("^/", "", any_path)


def undraft(pathlike):
    """
    Remove the leading `_` from a path, if any.
    """
    path = PurePath(pathlike)
    if path.stem.startswith("_"):
        return path.with_name(re.sub(r'^_', "", path.name))
    else:
        return path


def relative_to(tlds):
    """
    Create a mapping function that will transform pathlike so it is
    relative to some top-level directories (tlds).
    """
    return lambda pathlike: str(PurePath(pathlike).relative_to(tlds))


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
    purepath = undraft(purepath)
    # Don't touch index pages
    if purepath.stem == "index":
        return purepath
    index_file = "index" + purepath.suffix
    index_path = PurePath(purepath.parent, purepath.stem, index_file)
    # Slug-ify and then convert slug string to path object.
    nice_path = PurePath(to_slug(index_path))
    return nice_path


def _get_ext(pathlike):
    return PurePath(pathlike).suffix


def _put_ext(pathlike, ext):
    return str(PurePath(pathlike).with_suffix(ext))


ext = Lens(_get_ext, _put_ext)


def ext_html(pathlike):
    """
    Set suffix `.html` on a pathlike.
    Return a path string.
    """
    return put(ext, pathlike, ".html")


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
    if purepath.name == "index.html":
        purepath = ensure_trailing_slash(purepath.parent)
    qualified = qualify_url(purepath, base=base)
    return qualified


def is_draft(pathlike):
    return PurePath(pathlike).name.startswith("_")


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


def is_sibling(path_a, path_b):
    """
    What is a sibling:

    foo/bar/baz.html
    foo/bar/bing.html

    What is not a sibling:

    foo/bar/boing/index.html
    """
    return (
        PurePath(path_a).parent == PurePath(path_b).parent
        and not is_index(path_b))


def filter_files(paths):
    """
    Given an iterable of paths, filter paths to just those which are
    file paths.
    """
    for pathlike in paths:
        path = Path(pathlike)
        if path.is_file():
            yield path


def glob_files(directory, glob):
    """
    Return files matching glob
    """
    return filter_files(Path(directory).glob(glob))


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