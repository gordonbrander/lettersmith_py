from commonmark import commonmark
from lettersmith.html import strip_html
from lettersmith import docs as Docs
from lettersmith.func import compose


markdown = commonmark
strip_markdown = compose(strip_html, markdown)
content = Docs.renderer(markdown)