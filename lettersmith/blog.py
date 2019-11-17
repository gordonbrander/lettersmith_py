"""
Tools for blogging
"""
from lettersmith.util import compose
from lettersmith import wikidoc
from lettersmith import absolutize
from lettersmith import templatetools
from lettersmith import permalink
from lettersmith import docs


def markdown_doc(base_url):
    """
    Handle typical transformations for a generic markdown doc.
    """
    return compose(
        absolutize.absolutize(base_url),
        wikidoc.render_docs_markdown(base_url),
        templatetools.add_templates,
        docs.uplift_frontmatter
    )


def page(base_url):
    """
    Performs typical transformations for a page.

    - Markdown
    - Absolutizes post links
    - Changes file extensions
    - Sets nice permalink
    - Adds templates in prep for Jinja rendering later
    """
    return compose(
        markdown_doc(base_url),
        permalink.page_permalink
    )


def post(base_url):
    """
    Performs typical transformations for a blog post.

    - Markdown
    - Absolutizes post links
    - Changes file extensions
    - Sets date-based permalink
    - Adds templates in prep for Jinja rendering later
    """
    return compose(
        markdown_doc(base_url),
        permalink.post_permalink
    )