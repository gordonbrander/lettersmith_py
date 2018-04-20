"""
Tools for making relative URLs absolute in doc content.
"""
import re
from lettersmith.util import replace
from lettersmith import path as pathtools

URL_ATTR = r"""(src|href)=["'](.*?)["']"""


def absolutize_doc_urls(doc, base="/"):
    """
    Absolutize URLs in content. Replaces any relative URLs in content
    that start with `/` and instead starts them with `base`.

    URLS are found by matching against `href=` and `src=`.
    """
    # Early return if base URL is just "/"
    if str(base) == "/":
        return doc

    def render_inner_match(match):
        attr = match.group(1)
        value = match.group(2)
        url = pathtools.qualify_url(value, base)
        return '{attr}="{url}"'.format(attr=attr, url=url)

    content = re.sub(
        URL_ATTR,
        render_inner_match,
        doc.content
    )

    return replace(doc, content=content)


def map_absolutize(docs, base_url="/"):
    # Early return if base URL is just "/"
    if str(base_url) == "/":
        return docs
    return (absolutize_doc_urls(doc, base_url) for doc in docs)