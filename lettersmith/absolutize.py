"""
Tools for making relative URLs absolute in doc content.
"""
import re
from lettersmith.util import replace
from lettersmith import path as pathtools


URL_ATTR = r"""(src|href)=["'](.*?)["']"""


def absolutize(docs, base_url="/"):
    """
    Absolutize URLs in content. Replaces any relative URLs in content
    that start with `/` and instead starts them with `base_url`.

    URLS are found by matching against `href=` and `src=`.
    """
    # Early return if base URL is just "/"
    if str(base_url) == "/":
        return docs

    def render_inner_match(match):
        attr = match.group(1)
        value = match.group(2)
        url = pathtools.qualify_url(value, base_url)
        return '{attr}="{url}"'.format(attr=attr, url=url)

    for doc in docs:
        content = re.sub(
            URL_ATTR,
            render_inner_match,
            doc.content
        )
        yield doc._replace(content=content)