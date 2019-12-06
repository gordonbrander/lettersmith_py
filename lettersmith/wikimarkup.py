"""
Render wikilinks in text.
"""
import re
from lettersmith.path import to_slug


_WIKILINK = r'\[\[([^\]]+)\]\]'
_TRANSCLUDE = r'^\[\[([^\]]+)\]\]$'


def _sub_wikilink_title(match):
    slug, title = _parse_wikilink(match.group(0))
    return title


def strip_wikilinks(text):
    """
    Strip markup from text
    """
    # Remove transcludes completely
    text = re.sub(_TRANSCLUDE, "", text, flags=re.MULTILINE)
    # Remove inline wikilinks, but leaves bare text
    text = re.sub(_WIKILINK, _sub_wikilink_title, text)
    return text


def _parse_wikilink(wikilink_str):
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
    return slug, text


def find_wikilinks(s):
    """
    Find all wikilinks in a string (if any)
    Returns an iterator of 2-tuples for slug, title.
    """
    for match in re.finditer(_WIKILINK, s):
        yield _parse_wikilink(match.group(0))


def renderer(render_wikilink):
    """
    Creates a renderer function
    """
    def _render_wikilink(match):
        slug, title = _parse_wikilink(match.group(0))
        return render_wikilink(slug, title, "inline")

    def _render_transclude(match):
        slug, title = _parse_wikilink(match.group(0))
        return render_wikilink(slug, title, "transclude")

    def render_text(text):
        text = re.sub(_TRANSCLUDE, _render_transclude, text, flags=re.MULTILINE)
        text = re.sub(_WIKILINK, _render_wikilink, text)
        return text

    return render_text