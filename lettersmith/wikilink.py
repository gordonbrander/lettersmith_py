"""
Tools for parsing and rendering `[[wikilinks]]`

To render wikilinks, I need:

- An index of all doc urls (to know if they exist)
- A regular expression to match links
- A base URL to root links to (optional, could just root to "/" and absolutize
  with another plugin)
"""
import re
from pathlib import PurePath
from os import path
from collections import namedtuple
from lettersmith import doc as Doc
from lettersmith.path import to_slug, to_url
from lettersmith.util import replace, get, index_many, expand


WIKILINK = r'\[\[([^\]]+)\]\]'
LINK_TEMPLATE = '<a href="{url}" class="wikilink">{text}</a>'
NOLINK_TEMPLATE = '<span class="nolink">{text}</span>'


Link = namedtuple("Link", ("id_path", "output_path", "title"))
Link.__doc__ = """
A namedtuple for representing a link entry — just a title and an id_path.
"""


Edge = namedtuple("Edge", ("tail", "head"))
Edge.__doc__ = """
A directed edge that points from one link to another.
"""


@get.register(Link)
def get_link(link, key, default=None):
    return getattr(link, key, default)


def parse_wikilink(wikilink_str):
    """
    Given a `[[WikiLink]]` or a `[[wikilink | Title]]`, return a
    tuple of `(wikilink, Title)`.

    Supports both piped and non-piped forms.
    """
    inner = wikilink_str.strip('[] ')
    try:
        _slug, _text = inner.split("|")
        slug = to_slug(_slug.strip())
        text = _text.strip()
    except ValueError:
        text = inner.strip()
        slug = to_slug(text)
    return (slug, text)


def find_wikilinks(s):
    """
    Find all wikilinks in a string (if any)
    Returns an iterator of 2-tuples for slug, title.
    """
    for match in re.finditer(WIKILINK, s):
        yield parse_wikilink(match.group(0))


def _render_strip_wikilink(match):
    slug, text = parse_wikilink(match.group(0))
    return text


def strip_wikilinks(s):
    """
    Find all wikilinks in a string (if any)
    and strips them, replacing them with their plaintext equivalent.
    """
    return re.sub(WIKILINK, _render_strip_wikilink, s)


def render_wikilinks(
    docs,
    base_url="/",
    link_template=LINK_TEMPLATE, nolink_template=NOLINK_TEMPLATE
):
    """
    `[[wikilink]]` is replaced with a link to a stub with the same title
    (case insensitive), using the `link_template`.
    If no stub exists with that title it will be rendered
    using `nolink_template`.
    """
    docs = tuple(docs)
    slug_to_link = index_slugs(docs)

    def render_inner_match(match):
        slug, text = parse_wikilink(match.group(0))
        try:
            link = slug_to_link[slug]
            url = to_url(link.output_path, base=base_url)
            return link_template.format(url=url, text=text)
        except KeyError:
            return nolink_template.format(text=text)

    for doc in docs:
        content = re.sub(
            WIKILINK,
            render_inner_match,
            doc.content
        )
        yield replace(doc, content=content)


def index_slugs(docs):
    return {
        to_slug(doc.title): Link(doc.id_path, doc.output_path, doc.title)
        for doc in docs
    }


def _extract_links(content, slug_to_link):
    wikilinks = frozenset(find_wikilinks(content))
    for slug, title in wikilinks:
        try:
            yield slug_to_link[slug]
        except KeyError:
            pass


def _expand_edges(doc, slug_to_link):
    tail = Link(doc.id_path, doc.output_path, doc.title)
    for head in _extract_links(doc.content, slug_to_link):
        yield Edge(tail, head)


def collect_edges(docs):
    docs = tuple(docs)
    slug_to_link = index_slugs(docs)
    return expand(_expand_edges, docs, slug_to_link)


def _index_by_link(edge):
    return edge.tail.id_path, edge.head


def _index_by_backlink(edge):
    return edge.head.id_path, edge.tail


_EMPTY_TUPLE = tuple()


def annotate_links(docs):
    """
    Annotate docs with links and backlinks.

    Returns an iterator for docs with 2 new meta fields: links and backlinks.
    Each contains a tuple of `Link` namedtuples.
    """
    docs = tuple(docs)
    edges = tuple(collect_edges(docs))
    link_index = index_many(_index_by_link(edge) for edge in edges)
    backlink_index = index_many(_index_by_backlink(edge) for edge in edges)
    for doc in docs:
        yield Doc.replace_meta(
            doc,
            links=tuple(link_index.get(doc.id_path, _EMPTY_TUPLE)),
            backlinks=tuple(backlink_index.get(doc.id_path, _EMPTY_TUPLE))
        )