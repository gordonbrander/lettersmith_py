"""
HTML markup -- a very unfancy markup language that automatically wraps
bare lines with `<p>` tags, but only if they don't contain a
block-level element.

Example:

    Bare lines are wrapped in paragraph tags.

    Blank spaces are ignored.

    You can use HTML like <b>bold</b>, or <i>italic</i> in paragraphs.

    <div>
        Indented lines, or lines containing block-level elements, will
        not be wrapped.
    </div>

    That's it!
"""
import re
from collections import namedtuple
from lettersmith.stringtools import first_sentence
from lettersmith import docs as Docs


def strip_html(html_str):
    """Remove html tags from a string."""
    return re.sub('<[^<]+?>', '', html_str)


def get_summary(doc):
    """
    Get summary for doc. Uses "summary" meta field if it exists.
    Otherwise, generates a summary by truncating doc content.
    """
    try:
        return strip_html(doc.meta["summary"])
    except KeyError:
        return first_sentence(strip_html(doc.content))


class RenderError(Exception):
    pass


Token = namedtuple("Token", ("type", "body"))
Token.__doc__ = """
A parsed token from the markup.
"""

_BLOCK_ELS = r"</?(address|article|aside|blockquote|br|details|dialog|dd|div|dl|dt|fieldset|figcaption|figure|footer|form|h1|h2|h3|h4|h5|h6|header|hgroup|hr|li|main|nav|ol|p|pre|section|table|ul)\b[^>]*>"


def _tokenize(lines):
    """
    Turn lines into tagged tokens.
    """
    for line in lines:
        line_clean = line.strip()
        if line_clean is "":
            pass
        elif line.startswith("  "):
            yield Token("html", line_clean)
        elif re.match(_BLOCK_ELS, line):
            yield Token("html", line_clean)
        else:
            yield Token("p", line_clean)


def _render_token(token):
    """
    Render HTML tokens. This markup language is very simple, so we only
    have two.
    """
    if token.type is "html":
        return token.body
    elif token.type is "p":
        return "<p>{}</p>".format(token.body)
    else:
        raise RenderError("Unknown token type {}".format(token.type))


def render_html(text):
    """
    Renders text as HTML.
    """
    lines = text.splitlines()
    return "\n".join(_render_token(token) for token in _tokenize(lines))


content = Docs.renderer(render_html)