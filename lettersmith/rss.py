from pathlib import Path
from datetime import datetime
from voluptuous import Schema, Optional
from lettersmith.util import sort_by, filter_id_path, compose
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


group_schema = Schema({
    "match": str,
    "output_path": str,
    Optional("title", default="Feed"): str,
    Optional("description", default=""): str,
    Optional("author", default=""): str,
    Optional("nitems", default=24): int
})


schema = Schema({
    Optional("groups", default=[]): [group_schema]
})


def render_rss(docs,
    base_url, last_build_date, title, description, author):
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


def create_rss_feed(
    docs,
    output_path,
    base_url, last_build_date,
    title, description, author,
    nitems
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
    recent = most_recent(docs, nitems)
    content = render_rss(
        recent,
        base_url=base_url,
        last_build_date=last_build_date,
        title=title,
        description=description,
        author=author
    )
    return Doc.doc(
        id_path=output_path,
        output_path=output_path,
        created=last_build_date,
        modified=last_build_date,
        title=title,
        content=content
    )


def gen_rss_feed(docs, base_url, groups):
    docs = tuple(docs)
    def _group_to_feed(group):
        matching_docs = filter_id_path(docs, group["match"])
        return create_rss_feed(
            matching_docs,
            last_build_date=datetime.now(),
            base_url=base_url,
            output_path=group["output_path"],
            nitems=group["nitems"],
            title=group["title"],
            description=group["description"],
            author=group["author"]
        )
    return map(_group_to_feed, groups)