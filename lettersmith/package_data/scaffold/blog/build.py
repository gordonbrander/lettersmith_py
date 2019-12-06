#!/usr/bin/env python3
"""
A blog-aware Lettersmith build script. Modify it to your heart's content.
"""
from lettersmith import *

# Configuration
base_url = "http://yourwebsite.com"
site_title = "My very cool website"
site_description = "A very cool website"
site_author = "A very cool person"

# Load data directory
template_data = data.find("data")

# Load static and binary files
static = files.find("static/**/*")

# Load post docs and pipe through plugins
posts = pipe(
    docs.find("post/*.md"),
    blog.markdown_post(base_url),
    docs.sort_by_created,
    tuple
)

# Load page docs and pipe through plugins
pages = pipe(
    docs.find("page/*.md"),
    blog.markdown_page(base_url, relative_to="page")
)

posts_rss_doc = pipe(posts, rss.rss(
    base_url=base_url,
    title=site_title,
    description=site_description,
    author=site_author,
    output_path="posts.xml"
))

archive_doc = pipe(posts, archive.archive("archive/index.html"))
recent_posts = pipe(posts, stub.stubs, query.takes(5))

posts_and_pages = (*posts, *pages)

sitemap_doc = pipe(posts_and_pages, sitemap.sitemap(base_url))

context = {
    "rss_docs": (posts_rss_doc,),
    "recent": recent_posts,
    "site": {
        "title": site_title,
        "description": site_description,
        "author": site_author
    },
    "data": template_data,
    "base_url": base_url
}

rendered_docs = pipe(
    (sitemap_doc, posts_rss_doc, archive_doc, *posts_and_pages),
    jinjatools.jinja("template", base_url, context)
)

write(chain(static, rendered_docs), directory="public")

print("Done!")