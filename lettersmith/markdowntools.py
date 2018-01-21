from pathlib import PurePath
from markdown import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension

from lettersmith.util import merge, map_match
from lettersmith.path import has_ext


MD_LANG_EXTENSIONS=(GithubFlavoredMarkdownExtension(),)


MD_EXTENSIONS = (".md", ".markdown", ".mdown", ".txt")


def is_markdown_doc(doc):
    """
    Check if a document is a markdown document. Returns a bool.
    """
    return has_ext(doc["simple_path"], MD_EXTENSIONS)


def render_doc(doc, extensions=MD_LANG_EXTENSIONS):
    """
    Render markdown in content field of doc dictionary.
    Updates the output path to .html.
    Returns a new doc.
    """
    content = markdown(doc.get("content", ""), extensions=extensions)
    output_path = PurePath(doc["output_path"]).with_suffix(".html")
    return merge(doc, {
        "content": content,
        "output_path": str(output_path)
    })


def map_markdown(docs, extensions=MD_LANG_EXTENSIONS):
    """
    Given an iterable of docs, return a generator that will yield
    markdown docs rendered to HTML. Things that aren't markdown docs
    will be yielded untouched. 
    """
    return map_match(is_markdown_doc, render_doc, docs, extensions=extensions)