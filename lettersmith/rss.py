from pathlib import Path
from itertools import islice
from datetime import datetime
from lettersmith.util import sort_by
from lettersmith.jinjatools import create_env
from lettersmith.path import to_url
from lettersmith import doc as Doc

MODULE_PATH = Path(__file__).parent
TEMPLATE_PATH = Path(MODULE_PATH, "package_data", "template")

FILTERS = {
  "to_url": to_url
}


def render_rss(stubs,
  base_url="/", last_build_date=None,
  title="Feed", description="", author=""):
  context = {
    "generator": "Lettersmith",
    "base_url": base_url,
    "title": title,
    "description": description,
    "author": author,
    "last_build_date":
      last_build_date if last_build_date is not None else datetime.now()
  }
  env = create_env(str(TEMPLATE_PATH), context=context, filters=FILTERS)
  rss_template = env.get_template("rss.xml")
  return rss_template.render({
    "stubs": stubs  
  })


def most_recent_n(stubs, nitems=24):
  return islice(sort_by(stubs, "created", reverse=True), nitems)  


def gen_rss(stubs, output_path,
  base_url="/", last_build_date=None,
  title="Feed", description="", author=""):
  """
  Yields an RSS doc
  """
  now = datetime.now()
  content = render_rss(
    stubs,
    base_url=base_url,
    last_build_date=last_build_date,
    title=title,
    description=description,
    author=author
  )
  return Doc.doc(
    id_path=output_path,
    output_path=output_path,
    created=now,
    modified=now,
    content=content
  )