from pathlib import PurePath
from markdown import markdown as md
from mdx_gfm import GithubFlavoredMarkdownExtension
from lettersmith.html import strip_html
from lettersmith.doc import annotate_exceptions


def markdown(s):
    """
    Just a wrapper for our house flavor of markdown.
    We use Github-flavored markdown as a base.
    """
    return md(s, extensions=(GithubFlavoredMarkdownExtension(),))


def strip_markdown(s):
    """
    Strip markdown, returning a bare string. This is useful for
    generating summaries of markdown docs.
    """
    return strip_html(markdown(s))


@annotate_exceptions
def render_doc(doc):
    """
    Render markdown in content field of doc dictionary.
    Updates the output path to .html.
    Returns a new doc.
    """
    content = markdown(doc.content)
    output_path = PurePath(doc.output_path).with_suffix(".html")
    return doc._replace(
        content=content,
        output_path=str(output_path)
    )


def content(docs):
    """
    Markdown rendering plugin
    """
    for doc in docs:
        yield render_doc(doc)