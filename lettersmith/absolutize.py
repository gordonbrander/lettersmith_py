"""
Tools for making relative URLs absolute in doc content.
"""
import re
from lettersmith.docs import renderer
from lettersmith.func import composable
from lettersmith import path as pathtools


URL_ATTR = r"""(src|href)=["'](.*?)["']"""


def absolutize(base_url):
    """
    Absolutize URLs in content. Replaces any relative URLs in content
    that start with `/` and instead starts them with `base_url`.

    URLS are found by matching against `href=` and `src=`.
    """
    def render_inner_match(match):
        attr = match.group(1)
        value = match.group(2)
        url = pathtools.qualify_url(value, base_url)
        return '{attr}="{url}"'.format(attr=attr, url=url)

    @renderer
    def render(content):
        """
        Absolutize URLs in doc content fields.
        """
        return re.sub(URL_ATTR, render_inner_match, content)
    return render