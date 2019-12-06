from pathlib import Path
from datetime import datetime
from lettersmith.jinjatools import FileSystemEnvironment
from lettersmith.path import to_url
from lettersmith import doc as Doc
from lettersmith.docs import most_recent
from lettersmith.html import get_summary
from lettersmith.stringtools import first_sentence
from lettersmith.func import composable


MODULE_PATH = Path(__file__).parent
TEMPLATE_PATH = Path(MODULE_PATH, "package_data", "template")


FILTERS = {
    "get_summary": get_summary,
    "to_url": to_url
}

def render_rss(
    docs,
    base_url,
    last_build_date,
    title,
    description,
    author
):
    context = {
        "generator": "Lettersmith",
        "base_url": base_url,
        "title": title,
        "description": description,
        "author": author,
        "last_build_date": last_build_date
    }
    env = FileSystemEnvironment(
        str(TEMPLATE_PATH),
        context=context,
        filters=FILTERS
    )
    rss_template = env.get_template("rss.xml")
    return rss_template.render({
        "docs": docs
    })


_most_recent_24 = most_recent(24)


@composable
def rss(
    docs,
    base_url,
    title,
    description,
    author,
    output_path="rss.xml",
    last_build_date=None
):
    """
    Given an iterable of docs and some details, returns an
    RSS doc.
    """
    last_build_date = (
        last_build_date
        if last_build_date is not None
        else datetime.now()
    )
    recent = _most_recent_24(docs)
    content = render_rss(
        recent,
        base_url=base_url,
        last_build_date=last_build_date,
        title=title,
        description=description,
        author=author
    )
    return Doc.create(
        id_path=output_path,
        output_path=output_path,
        created=last_build_date,
        modified=last_build_date,
        title=title,
        content=content
    )
