from pathlib import Path
from datetime import datetime
from lettersmith.util import sort_by, filter_id_path
from lettersmith.jinjatools import FileSystemEnvironment
from lettersmith.path import to_url, to_slug
from lettersmith import doc as Doc
from lettersmith.docs import most_recent

MODULE_PATH = Path(__file__).parent
TEMPLATE_PATH = Path(MODULE_PATH, "package_data", "template")

FILTERS = {
    "summary": Doc.summary,
    "to_url": to_url
}

def render_rss(docs,
    base_url, last_build_date, title, description, author, read_more):
    context = {
        "generator": "Lettersmith",
        "base_url": base_url,
        "title": title,
        "description": description,
        "author": author,
        "last_build_date": last_build_date,
        "read_more": read_more
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


def create_rss_feed(docs, output_path,
    base_url="/", last_build_date=None,
    title="RSS Feed", description="", author="",
    read_more="Read more&hellip;", nitems=24):
    """
    Given an iterable of docs and some details, returns an
    RSS doc.
    """
    last_build_date = (
        last_build_date
        if last_build_date is not None
        else datetime.now()
    )
    recent = most_recent(docs, nitems)
    content = render_rss(
        recent,
        base_url=base_url,
        last_build_date=last_build_date,
        title=title,
        description=description,
        author=author,
        read_more=read_more
    )
    return Doc.doc(
        id_path=output_path,
        output_path=output_path,
        created=last_build_date,
        modified=last_build_date,
        title=title,
        content=content
    )


def gen_rss_feed(docs, groups,
    base_url="/", last_build_date=None,
    read_more="Read more&hellip;", nitems=24,
    title="RSS Feed", description="", author=""
):
    def _map_items(pair):
        glob, group = pair
        matching_docs = filter_id_path(docs, glob)
        return create_rss_feed(
            matching_docs,
            output_path=group["output_path"],
            base_url=base_url,
            last_build_date=last_build_date,
            read_more=read_more,
            nitems=nitems,
            title=group.get("title", title),
            description=group.get("description", description),
            author=group.get("author", author)
        )
    return map(_map_items, groups.items())