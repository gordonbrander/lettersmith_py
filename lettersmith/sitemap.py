from pathlib import Path
from datetime import datetime
from itertools import islice
from lettersmith import doc as Doc
from lettersmith.jinjatools import FileSystemEnvironment
from lettersmith.path import to_url
from lettersmith.func import composable

MODULE_PATH = Path(__file__).parent
TEMPLATE_PATH = Path(MODULE_PATH, "package_data", "template")

FILTERS = {
    "to_url": to_url
}


def render_sitemap(docs,
    base_url="/", last_build_date=None,
    title="Feed", description="", author=""):
    context = {"base_url": base_url}
    env = FileSystemEnvironment(
        str(TEMPLATE_PATH),
        context=context,
        filters=FILTERS
    )
    template = env.get_template("sitemap.xml")
    return template.render({"docs": docs})


@composable
def sitemap(docs, base_url):
    """
    Returns a sitemap doc
    """
    # The sitemap spec limits each sitemap to 50k entries.
    # https://www.sitemaps.org/protocol.html
    docs_50k = islice(docs, 50000)
    output_path = "sitemap.xml"
    now = datetime.now()
    content = render_sitemap(docs_50k, base_url=base_url)
    return Doc.create(
        id_path=output_path,
        output_path=output_path,
        created=now,
        modified=now,
        content=content
    )