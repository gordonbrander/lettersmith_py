from pathlib import Path
from datetime import datetime
from itertools import islice
from lettersmith import doc as Doc
from lettersmith.jinjatools import create_env
from lettersmith.path import to_url

MODULE_PATH = Path(__file__).parent
TEMPLATE_PATH = Path(MODULE_PATH, "package_data", "template")

FILTERS = {
  "to_url": to_url
}


def render_sitemap(stubs,
  base_url="/", last_build_date=None,
  title="Feed", description="", author=""):
  context = {"base_url": base_url}
  env = create_env(str(TEMPLATE_PATH), context=context, filters=FILTERS)
  template = env.get_template("sitemap.xml")
  return template.render({"stubs": stubs})


def gen_sitemap(stubs, base_url="/"):
  """
  Returns a sitemap doc
  """
  # The sitemap spec limits each sitemap to 50k entries.
  # https://www.sitemaps.org/protocol.html
  stubs_50k = islice(stubs, 50000)
  output_path = "sitemap.xml"
  now = datetime.now()
  content = render_sitemap(stubs_50k, base_url=base_url)
  return Doc.doc(
    id_path=output_path,
    output_path=output_path,
    created=now,
    modified=now,
    content=content
  )