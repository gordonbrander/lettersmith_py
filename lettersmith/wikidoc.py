"""
Wiki HTML -- a very simple markup language for wikilinks.

Example:

    Bare lines are wrapped in paragraphs.

    Blank spaces are ignored.

    You can use HTML like <b>bold</b>, or <i>italic</i> text.

    Lines with <div>block els</div> will not get wrapped.

        <div>
            If you indent a line, it will not get wrapped
            in a paragraph
        </div>

    [[Wikilinks]] also work. It's up to you to do something with them by
    implementing a function for the compiler.

    [[Transclusion wikilink]]

    A bare wikilink on a single line, like the one above is treated
    as a transclude. You can render something fancier here, like a
    `<portal>`.
"""
import re
from collections import namedtuple
from lettersmith import doc as Doc
from lettersmith import link as Link
from lettersmith import html
from lettersmith import wikimarkup
from lettersmith import markdowntools
from lettersmith.path import to_slug, to_url
from lettersmith.util import index_many, expand, compose, composable
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


def _annotate_summary(read_summary):
    """
    Render a summary from content using `read_summary` and set it on
    `doc.meta["summary"]`.

    If doc already has a `doc.meta["summary"]` it will leave it alone.
    """
    def annotate_summary(docs):
        for doc in docs:
            if doc.meta.get("summary"):
                yield doc
            else:
                yield Doc.replace_meta(doc, summary=read_summary(doc.content))
    return annotate_summary


annotate_summary_html = _annotate_summary(read_summary_html)
annotate_summary_markdown = _annotate_summary(read_summary_markdown)


def index_slugs(docs):
    return {
        to_slug(doc.title): Link.from_doc(doc)
        for doc in docs
    }


def _extract_links(content, slug_to_link):
    wikilinks = frozenset(wikimarkup.find_wikilinks(content))
    for slug, title in wikilinks:
        try:
            yield slug_to_link[slug]
        except KeyError:
            pass


def _expand_edges(doc, slug_to_link):
    tail = Link.from_doc(doc)
    for head in _extract_links(doc.content, slug_to_link):
        yield Link.Edge(tail, head)


def _collect_edges(docs):
    docs = tuple(docs)
    slug_to_link = index_slugs(docs)
    return expand(_expand_edges, docs, slug_to_link)


def _index_by_link(edge):
    return edge.tail.id_path, edge.head


def _index_by_backlink(edge):
    return edge.head.id_path, edge.tail


def annotate_links(docs):
    """
    Annotate docs with links and backlinks.

    Returns an iterator for docs with 2 new meta fields: links and backlinks.
    Each contains a tuple of `Link` namedtuples.
    """
    docs = tuple(docs)
    edges = tuple(_collect_edges(docs))
    link_index = index_many(_index_by_link(edge) for edge in edges)
    backlink_index = index_many(_index_by_backlink(edge) for edge in edges)
    empty = tuple()
    for doc in docs:
        yield Doc.replace_meta(
            doc,
            links=tuple(link_index.get(doc.id_path, empty)),
            backlinks=tuple(backlink_index.get(doc.id_path, empty))
        )


_LINK_TEMPLATE = '<a href="{url}" class="wikilink">{title}</a>'
_NOLINK_TEMPLATE = '<span class="nolink">{title}</span>'
_TRANSCLUDE_TEMPLATE = '''<aside class="transclude">
  <a class="transclude-link" href="{url}">
    <h1 class="transclude-title">{title}</h1>
    <div class="transclude-summary">{summary}</div>
  </a>
</aside>'''


@composable
def render_wikilinks(
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
    slug_to_link = index_slugs(docs)

    def render_wikilink(slug, title, type):
        if type is "transclude":
            try:
                link = slug_to_link[slug]
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
                link = slug_to_link[slug]
                url = to_url(link.output_path, base=base_url)
                return link_template.format(url=url, title=title)
            except KeyError:
                return nolink_template.format(title=title)

    render_wikilinks = wikimarkup.renderer(render_wikilink)

    for doc in docs:
        content = render_wikilinks(doc.content)
        yield doc._replace(content=content)


def render_docs_markdown(
    base_url,
    link_template=_LINK_TEMPLATE,
    nolink_template=_NOLINK_TEMPLATE,
    transclude_template=_TRANSCLUDE_TEMPLATE
):
    return compose(
        markdowntools.render_docs,
        render_wikilinks(
            base_url,
            link_template,
            nolink_template,
            transclude_template
        ),
        annotate_links,
        annotate_summary_markdown
    )


def render_docs_html(
    base_url,
    link_template=_LINK_TEMPLATE,
    nolink_template=_NOLINK_TEMPLATE,
    transclude_template=_TRANSCLUDE_TEMPLATE
):
    return compose(
        html.render_docs,
        render_wikilinks(
            base_url,
            link_template,
            nolink_template,
            transclude_template
        ),
        annotate_links,
        annotate_summary_html
    )