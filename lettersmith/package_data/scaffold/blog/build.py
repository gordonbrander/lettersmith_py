#!/usr/bin/env python3
"""
A blog-aware Lettersmith build script. Modify it to your heart's content.
"""
from lettersmith import *
from lettersmith.util import pipe

# Configuration
base_url = "http://yourwebsite.com"
site_title = "My very cool website"
site_description = "A very cool website"
site_author = "A very cool person"

# Load data directory
template_data = data.find("data")

posts = pipe(doc.find("posts", "*.md"), blog.post(base_url), tuple)
pages = pipe(doc.find("pages", "*.md"), blog.page(base_url))

posts_rss_doc = pipe(posts, rss.rss(
    base_url=base_url,
    title=site_title,
    description=site_description,
    author=site_author,
    output_path="posts.xml"
))

tag_index = taxonomy.index_tags(posts)

posts_and_pages = (*posts, *pages)

sitemap_doc = pipe(posts_and_pages, sitemap.sitemap(base_url))

all_docs = (sitemap_doc, posts_rss_doc, *posts_and_pages)

id_path_index = {doc.id_path: doc for doc in all_docs}

context = {
    "rss_docs": (posts_rss_doc,),
    "index": {
        "tags": tag_index,
        "id_path": id_path_index
    },
    "site": {
        "title": site_title,
        "description": site_description,
        "author": site_author
    },
    "data": template_data,
    "base_url": base_url
}

templated_docs = pipe(
    all_docs,
    jinjatools.jinja("theme", base_url, context)
)

docs.write(templated_docs, output_path="public")

print("Done!")