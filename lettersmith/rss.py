from pathlib import Path
from itertools import islice
from datetime import datetime
from lettersmith.util import sort_by, expand, decorate_group_matching_id_path
from lettersmith.jinjatools import FileSystemEnvironment
from lettersmith.path import to_url, to_slug
from lettersmith import doc as Doc

MODULE_PATH = Path(__file__).parent
TEMPLATE_PATH = Path(MODULE_PATH, "package_data", "template")

FILTERS = {
    "to_url": to_url
}

def render_rss(stubs,
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
        "stubs": stubs
    })


def most_recent(stubs, nitems=24):
    return islice(sort_by(stubs, "created", reverse=True), nitems)  


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
    recent_stubs = most_recent(stubs, nitems)
    content = render_rss(
        recent_stubs,
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


def gen_rss_feed(docs, options,
    base_url="/", last_build_date=None, author="",
    read_more="Read more&hellip;"
):
    def _gen_rss_feed(pair):
        glob, options = pair
        matching_docs = filter_id_path(docs, glob)
        return create_rss_feed(
            matching_docs,
            base_url=base_url,
            last_build_date=last_build_date,
            author=author,
            read_more=read_more,
            **options
        )
    return map(_gen_rss_feed, options.items())