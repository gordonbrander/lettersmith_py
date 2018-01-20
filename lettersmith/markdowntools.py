from pathlib import PurePath
from markdown import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension

from lettersmith.util import merge
from lettersmith.path import has_ext


MD_LANG_EXTENSIONS=(GithubFlavoredMarkdownExtension(),)


MD_EXTENSIONS = (".md", ".markdown", ".mdown", ".txt")


def is_markdown_doc(doc):
    return has_ext(doc["simple_path"], MD_EXTENSIONS)


def render_doc(doc, extensions=MD_LANG_EXTENSIONS):
    """Render markdown in content field of doc dictionary"""
    content = markdown(doc.get("content", ""), extensions=extensions)
    output_path = PurePath(doc["output_path"]).with_suffix(".html")
    return merge(doc, {
        "content": content,
        "output_path": str(output_path)
    })


def map_markdown(docs, extensions=MD_LANG_EXTENSIONS):
    return (
        render_doc(doc, extensions=extensions)
        for doc in docs
        if is_markdown_doc(doc)
    )