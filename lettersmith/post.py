"""
Wraps up a handful of smaller plugins into a 
"""
from lettersmith import markdowntools
from lettersmith import absolutize
from lettersmith import templatetools
from lettersmith import wikilink
from lettersmith import permalink
from lettersmith import docs as Docs


def render_posts(docs, base_url):
    """
    Performs typical transformations for a blog post or page.

    - Markdown
    - Absolutizes post links
    - Changes file extensions
    - Sets nice permalink
    - Adds templates in prep for Jinja rendering later
    """
    docs = markdowntools.parse_markdown(docs)
    docs = absolutize.absolutize(docs, base_url)
    docs = Docs.change_ext(docs, ".html")
    docs = templatetools.add_templates(docs)
    return docs
