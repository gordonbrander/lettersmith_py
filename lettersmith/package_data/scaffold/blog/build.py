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

post = blog.markdown_post(base_url)
posts = tuple(post(doc.find("posts", "*.md")))

page = blog.markdown_page(base_url)
pages = page(doc.find("pages", "*.md"))

posts_rss_doc = pipe(posts, rss.rss(
    base_url=base_url,
    title=site_title,
    description=site_description,
    author=site_author,
    output_path="posts.xml"
))

tag_index = taxonomy.index_tags(posts)

posts_and_pages = (*posts, *pages)

create_sitemap = sitemap.sitemap(base_url)
sitemap_doc = create_sitemap(posts_and_pages)

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

render_template = jinjatools.jinja("theme", base_url, context)
template_docs = render_template(all_docs)

docs.write(template_docs, output_path="public")

print("Done!")