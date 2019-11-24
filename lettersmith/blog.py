"""
Tools for blogging
"""
from lettersmith.func import compose
from lettersmith import wikidoc
from lettersmith import absolutize
from lettersmith import permalink
from lettersmith import docs as Docs


def markdown_doc(base_url):
    """
    Handle typical transformations for a generic markdown doc.
    """
    return compose(
        absolutize.absolutize(base_url),
        wikidoc.content_markdown(base_url),
        Docs.autotemplate,
        Docs.uplift_frontmatter
    )


def markdown_page(base_url, relative_to="."):
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
        permalink.rel_page_permalink(relative_to)
    )


def markdown_post(base_url):
    """
    Performs typical transformations for a blog post.

    - Markdown
    - Wikilinks
    - Absolutizes post links
    - Changes file extensions
    - Sets date-based permalink
    - Adds templates in prep for Jinja rendering later
    """
    return compose(
        markdown_doc(base_url),
        permalink.post_permalink
    )


def html_doc(base_url):
    """
    Handle typical transformations for a generic html doc.
    """
    return compose(
        absolutize.absolutize(base_url),
        wikidoc.content_html(base_url),
        Docs.autotemplate,
        Docs.uplift_frontmatter
    )


def html_page(base_url, relative_to="."):
    """
    Performs typical transformations for a page.

    - Wrap non-HTML lines with paragraph tags.
    - Wikilinks
    - Absolutizes post links
    - Changes file extensions
    - Sets nice permalink
    - Adds templates in prep for Jinja rendering later
    """
    return compose(
        html_doc(base_url),
        permalink.rel_page_permalink(relative_to)
    )


def html_post(base_url):
    """
    Performs typical transformations for a blog post.

    - Wrap non-HTML lines with paragraph tags.
    - Wikilinks
    - Absolutizes post links
    - Changes file extensions
    - Sets date-based permalink
    - Adds templates in prep for Jinja rendering later
    """
    return compose(
        html_doc(base_url),
        permalink.post_permalink
    )