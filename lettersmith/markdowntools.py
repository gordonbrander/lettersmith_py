from pathlib import PurePath
from markdown import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension

from lettersmith.util import replace, get_deep
from lettersmith.path import has_ext
from lettersmith.cursor import extra_reader


MD_LANG_EXTENSIONS=(GithubFlavoredMarkdownExtension(),)


MD_EXTENSIONS = [".md", ".markdown", ".mdown", ".txt"]


def house_markdown(s):
    """
    Just a wrapper for our house flavor of markdown.
    We use Github-flavored markdown as a base.
    """
    return markdown(s, extensions=MD_LANG_EXTENSIONS)


def is_markdown_doc(doc):
    """
    Check if a document is a markdown document. Returns a bool.
    """
    return has_ext(doc.id_path, MD_EXTENSIONS)


def render_doc(doc, extensions=MD_LANG_EXTENSIONS):
    """
    Render markdown in content field of doc dictionary.
    Updates the output path to .html.
    Returns a new doc.
    """
    if is_markdown_doc(doc):
        content = markdown(doc.content, extensions=extensions)
        output_path = PurePath(doc.output_path).with_suffix(".html")
        return replace(doc, content=content, output_path=str(output_path))
    else:
        return doc


@extra_reader
def read_markdown_config(config):
    """
    Read markdown configuration options from top-level config object.
    """
    return {
        "extensions": get_deep(
            config,
            ("markdown", "lang_extensions"),
            MD_LANG_EXTENSIONS
        )
    }


map_markdown_plugin = read_markdown_config(render_doc)