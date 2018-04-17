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
from lettersmith import doc as Doc
from lettersmith.path import to_slug, to_url
from lettersmith.util import put


WIKILINK = r'\[\[([^\]]+)\]\]'
LINK_TEMPLATE = '<a href="{url}" class="wikilink">{text}</a>'
NOLINK_TEMPLATE = '<span title="Page doesn\'t exist yet" class="nolink">{text}</span>'


def parse_inner(tag_inner):
    """
    Right now this just strips text. It may get fancier if we introduce
    pipes for vanity naming wikilinks.
    """
    return tag_inner.strip()


def render_doc(doc, wikilink_index,
    link_template=LINK_TEMPLATE, nolink_template=NOLINK_TEMPLATE):
    """Render wikilinks in doc content field."""
    def render_inner_match(match):
        inner = match.group(1)
        text = parse_inner(inner)
        try:
            url = wikilink_index[to_slug(text)]
            return link_template.format(url=url, text=text)
        except KeyError:
            return nolink_template.format(text=text)

    content = re.sub(
        WIKILINK,
        render_inner_match,
        doc["contents"]
    )

    return put(doc, "contents", content)


def uplift_wikilinks(doc):
    """
    Find all wikilinks in doc and assign them to a wikilinks property of doc.
    """
    matches = re.finditer(WIKILINK, doc["contents"])
    wikilinks = (match.group(1) for match in matches)
    slugs = tuple(to_slug(wikilink) for wikilink in wikilinks)
    return Doc.put_meta(doc, "wikilinks", slugs)


def index_wikilinks(docs, base="/"):
    """
    Reduce an iterator of docs to a slug-to-url index.
    """
    return {
        to_slug(doc["title"]): to_url(doc["output_path"], base=base)
        for doc in docs
    }


def index_backlinks(entries):
    """
    Index all backlinks in an iterable of docs. This assumes you have
    already uplifted wikilinks from content with `uplift_wikilinks`.
    """
    # Create an index of `slug: [slugs]`
    wikilink_index = {
        to_slug(entry["title"]): entry
        for entry in entries
        if "wikilinks" in entry["meta"]
    }
    backlink_index = {}
    for entry in wikilink_index.values():
        for slug in frozenset(entry["meta"]["wikilinks"]):
            try:
                to_path = wikilink_index[slug]["id_path"]
                if to_path not in backlink_index:
                    backlink_index[to_path] = []
                backlink_index[to_path].append(entry)
            except KeyError:
                pass
    return backlink_index


def map_wikilinks(docs, wikilink_index,
    link_template=LINK_TEMPLATE, nolink_template=NOLINK_TEMPLATE):
    """
    Return a generator that will yield docs with `[[wikilinks]]` rendered as
    HTML links.
    """
    for doc in docs:
        yield render_doc(doc, wikilink_index, link_template, nolink_template)
