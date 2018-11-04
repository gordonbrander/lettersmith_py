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
from lettersmith.util import replace, get


WIKILINK = r'\[\[([^\]]+)\]\]'
LINK_TEMPLATE = '<a href="{url}" class="wikilink">{text}</a>'
NOLINK_TEMPLATE = '<span class="nolink">{text}</span>'


Link = namedtuple("Link", ("id_path", "output_path", "title"))
Link.__doc__ = """
A namedtuple for representing a link entry — just a title and an id_path.
"""

@get.register(Link)
def get_link(link, key, default=None):
    return getattr(link, key, default)

def link_from_stub(stub):
    return Link(stub.id_path, stub.output_path, stub.title)


def _index_slug_to_url(stubs, base_url="/"):
    """
    Reduce an iterator of docs to a slug-to-url index.
    """
    return {
        to_slug(stub.title): to_url(stub.output_path, base=base_url)
        for stub in stubs
    }


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


def doc_renderer(stubs,
    base_url="",
    link_template=LINK_TEMPLATE, nolink_template=NOLINK_TEMPLATE):
    """
    Given a tuple of stubs, returns a doc rendering function that will
    render all `[[wikilinks]]` to HTML links.

    `[[wikilink]]` is replaced with a link to a stub with the same title
    (case insensitive), using the `link_template`.
    If no stub exists with that title it will be rendered
    using `nolink_template`.
    """
    slug_to_url = _index_slug_to_url(stubs, base_url)
    def render_inner_match(match):
        slug, text = parse_wikilink(match.group(0))
        try:
            url = slug_to_url[slug]
            return link_template.format(url=url, text=text)
        except KeyError:
            return nolink_template.format(text=text)

    def render_doc(doc):
        """
        Render a doc's wikilinks to HTML links.

        If a `[[wikilink]]` exists in the index, it will be rendered as an
        HTML link. However, if it doesn't exist, it will be rendered
        using `nolink_template`.
        """
        content = re.sub(
            WIKILINK,
            render_inner_match,
            doc.content
        )
        return replace(doc, content=content)

    return render_doc


def strip_doc_wikilinks(doc):
    """
    Strip wikilinks from doc content field.
    Useful for making stubs with a clean summary.
    """
    content = strip_wikilinks(doc.content)
    return replace(doc, content=content)


def uplift_wikilinks(doc):
    """
    Find all wikilinks in doc and assign them to a wikilinks property of doc.
    """
    wikilinks = find_wikilinks(doc.content)
    slugs = tuple(slug for slug, title in wikilinks)
    return Doc.replace_meta(doc, wikilinks=slugs)


def _index_backlinks(slug_index):
    """
    Index all backlinks in an iterable of docs. This assumes you have
    already uplifted wikilinks from content with `uplift_wikilinks`.
    """
    backlink_index = {}
    for stub in slug_index.values():
        for slug in frozenset(stub.meta["wikilinks"]):
            try:
                id_path = slug_index[slug].id_path
                if id_path not in backlink_index:
                    backlink_index[id_path] = []
                backlink_index[id_path].append(stub)
            except KeyError:
                pass
    return backlink_index


def collate_links(stubs):
    """
    Annotate stubs with links and backlinks. This assumes your stubs
    have uplifted wikilinks to meta with `uplift_wikilinks`.

    Returns an iterator for new stubs.
    Meta will have 2 new fields: `links` and `backlinks`, each containing
    a tuple of `Link` namedtuples.
    """
    slug_index = {
        to_slug(stub.title): stub
        for stub in stubs
    }
    backlink_index = _index_backlinks(slug_index)
    for stub in stubs:
        backlinks = tuple(
            link_from_stub(backlink_stub)
            for backlink_stub in backlink_index.get(stub.id_path, tuple())
        )
        slugs = frozenset(stub.meta["wikilinks"])
        links = tuple(
            link_from_stub(slug_index[slug])
            for slug in slugs
            if slug in slug_index
        )
        yield replace(
            stub,
            meta=replace(
                stub.meta,
                links=links,
                backlinks=backlinks
            )
        )