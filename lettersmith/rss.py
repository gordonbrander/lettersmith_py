from pathlib import Path
from itertools import islice
from datetime import datetime
from lettersmith.util import sort_by
from lettersmith.jinjatools import create_env
from lettersmith.path import to_url, to_slug
from lettersmith import doc as Doc

MODULE_PATH = Path(__file__).parent
TEMPLATE_PATH = Path(MODULE_PATH, "package_data", "template")

FILTERS = {
  "to_url": to_url
}

READ_MORE = "Read more&hellip;"


def render_rss(stubs,
  base_url="/", last_build_date=None,
  title="RSS Feed", description="", author="", read_more=None):
  context = {
    "generator": "Lettersmith",
    "base_url": base_url,
    "title": title,
    "description": description,
    "author": author,
    "last_build_date":
      last_build_date if last_build_date is not None else datetime.now(),
    "read_more": read_more if read_more is not None else READ_MORE
  }
  env = create_env(str(TEMPLATE_PATH), context=context, filters=FILTERS)
  rss_template = env.get_template("rss.xml")
  return rss_template.render({
    "stubs": stubs
  })


def most_recent(stubs, nitems=24):
  return islice(sort_by(stubs, "created", reverse=True), nitems)  


def gen_rss_feed(stubs, output_path,
  base_url="/", last_build_date=None,
  title="RSS Feed", description="", author="", read_more=None, nitems=24):
  """
  Given an iterable of stubs and some details, returns an
  RSS doc.
  """
  now = datetime.now()
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
    created=now,
    modified=now,
    title=title,
    content=content
  )