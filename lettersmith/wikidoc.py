"""
Tools for rendering wikilinks in content.
"""
import re
from collections import namedtuple
from lettersmith import doc as Doc
from lettersmith import docs as Docs
from lettersmith import stub as Stub
from lettersmith import edge as Edge
from lettersmith import html
from lettersmith import wikimarkup
from lettersmith import markdowntools
from lettersmith.path import to_slug, to_url
from lettersmith.util import index_sets, expand
from lettersmith.lens import lens_compose, key, get, put, over
from lettersmith.func import compose, composable
from lettersmith.stringtools import first_sentence


# Read a summary from an HTML text blob
read_summary_html = compose(
    first_sentence,
    wikimarkup.strip_wikilinks,
    html.strip_html
)

# Read a summary from a markdown text blob
read_summary_markdown = compose(
    first_sentence,
    wikimarkup.strip_wikilinks,
    markdowntools.strip_markdown
)


def _summary(read_summary):
    """
    Render a summary from content using `read_summary` and set it on
    `doc.meta["summary"]`.

    If doc already has a `doc.meta["summary"]` it will leave it alone.
    """
    def summary(docs):
        for doc in docs:
            if get(Doc.meta_summary, doc):
                yield doc
            else:
                yield put(Doc.meta_summary, doc, read_summary(doc.content))
    return summary


summary_html = _summary(read_summary_html)
summary_markdown = _summary(read_summary_markdown)


def _index_by_slug(docs):
    return {
        to_slug(doc.title): Stub.from_doc(doc)
        for doc in docs
    }


def _extract_links(content, slug_to_stub):
    wikilinks = frozenset(wikimarkup.find_wikilinks(content))
    for slug, title in wikilinks:
        try:
            yield slug_to_stub[slug]
        except KeyError:
            pass


def _expand_edges(doc, slug_to_stub):
    tail = Stub.from_doc(doc)
    for head in _extract_links(doc.content, slug_to_stub):
        yield Edge.Edge(tail, head)


def _collect_edges(docs):
    docs = tuple(docs)
    slug_to_stub = _index_by_slug(docs)
    return expand(_expand_edges, docs, slug_to_stub)


def _index_by_link(edge):
    return edge.tail.id_path, edge.head


def _index_by_backlink(edge):
    return edge.head.id_path, edge.tail


_empty = tuple()
meta_links = lens_compose(Doc.meta, key("links", _empty))
meta_backlinks = lens_compose(Doc.meta, key("backlinks", _empty))


def has_links(doc):
    return len(get(meta_links, doc)) > 0


def has_backlinks(doc):
    return len(get(meta_backlinks, doc)) > 0


def annotate_links(docs):
    """
    Annotate docs with links and backlinks.

    Returns an iterator for docs with 2 new meta fields: links and backlinks.
    Each contains a tuple of `Stub`s.
    """
    docs = tuple(docs)
    edges = tuple(_collect_edges(docs))
    link_index = index_sets(_index_by_link(edge) for edge in edges)
    backlink_index = index_sets(_index_by_backlink(edge) for edge in edges)
    empty = tuple()
    for doc in docs:
        backlinks = frozenset(backlink_index.get(doc.id_path, empty))
        links = frozenset(link_index.get(doc.id_path, empty))
        yield Doc.update_meta(doc, {
            "links": links,
            "backlinks": backlinks,
        })


_LINK_TEMPLATE = '<a href="{url}" class="wikilink">{title}</a>'
_NOLINK_TEMPLATE = '<span class="nolink">{title}</span>'
_TRANSCLUDE_TEMPLATE = '''<aside class="transclude">
  <a class="transclude-link" href="{url}">
    <h1 class="transclude-title">{title}</h1>
    <div class="transclude-summary">{summary}</div>
  </a>
</aside>'''


@composable
def content_wikilinks(
    docs,
    base_url,
    link_template=_LINK_TEMPLATE,
    nolink_template=_NOLINK_TEMPLATE,
    transclude_template=_TRANSCLUDE_TEMPLATE
):
    """
    `[[wikilink]]` is replaced with a link to a doc with the same title
    (case insensitive), using the `link_template`.

    If no doc exists with that title it will be rendered
    using `nolink_template`.
    """
    docs = tuple(docs)
    slug_to_stub = _index_by_slug(docs)

    def render_wikilink(slug, title, type):
        if type is "transclude":
            try:
                link = slug_to_stub[slug]
                url = to_url(link.output_path, base=base_url)
                return transclude_template.format(
                    url=url,
                    title=link.title,
                    summary=link.summary
                )
            except KeyError:
                return ""
        else:
            try:
                link = slug_to_stub[slug]
                url = to_url(link.output_path, base=base_url)
                return link_template.format(url=url, title=title)
            except KeyError:
                return nolink_template.format(title=title)

    render_wikilinks = wikimarkup.renderer(render_wikilink)

    for doc in docs:
        yield over(Doc.content, render_wikilinks, doc)


def content_markdown(
    base_url,
    link_template=_LINK_TEMPLATE,
    nolink_template=_NOLINK_TEMPLATE,
    transclude_template=_TRANSCLUDE_TEMPLATE
):
    """
    Render markdown and wikilinks.

    Also annotates doc meta with:

    - A summary
    - A list of links and backlinks.

    Example:

        Write _markdown_ like normal.

        - List item
        - List item
        - List item

        [[Wikilinks]] also work. They will be rendered as <a class="wikilink">Wikilinks</a>.

        [[Transclusion wikilink]]

        If you put a wikilink on it's own line, as above, it will be rendered as a rich snippet (transclude).
    """
    return compose(
        markdowntools.content,
        content_wikilinks(
            base_url,
            link_template,
            nolink_template,
            transclude_template
        ),
        annotate_links,
        summary_markdown
    )


def content_html(
    base_url,
    link_template=_LINK_TEMPLATE,
    nolink_template=_NOLINK_TEMPLATE,
    transclude_template=_TRANSCLUDE_TEMPLATE
):
    """
    Render html (wrap bare lines with paragraphs) and wikilinks.

    Also annotates doc meta with:

    - A summary
    - A list of links and backlinks.

    Example:

        Bare lines are wrapped in paragraphs.

        Blank spaces are ignored.

        You can use HTML like <b>bold</b>, or <i>italic</i> text.

        Lines with <div>block els</div> will not get wrapped.

            <div>
                If you indent a line, it will not get wrapped
                in a paragraph
            </div>

        [[Wikilinks]] also work. They will be rendered as <a class="wikilink">Wikilinks</a>.

        [[Transclusion wikilink]]

        If you put a wikilink on it's own line, as above, it will be rendered as a rich snippet (transclude).

    """
    return compose(
        html.content,
        content_wikilinks(
            base_url,
            link_template,
            nolink_template,
            transclude_template
        ),
        annotate_links,
        summary_html
    )