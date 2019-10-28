#!/usr/bin/env python3

"""
A blog-aware Lettersmith build script. Modify it to your heart's content.
"""
from lettersmith import *

# Configuration
base_url = "http://yourwebsite.com"
post_path = "posts"
page_path = "pages"
data_path = "data"
theme_path = "theme"
output_path = "public"
static_paths = ("theme/static", "static")
site_title= "My very cool website"
site_description = "A very cool website"
site_author = "A very cool person"
post_permalink_template = "{yyyy}/{mm}/{dd}/{name}/index.html"

# Load data directory
template_data = data.load_data_files(data_path)

# Load posts
posts = docs.load_matching(post_path, "*.md")
posts = post.render_posts(posts, base_url=base_url)
posts = permalink.replace_permalinks(posts, post_permalink_template)

# Load pages
pages = docs.load_matching(page_path, "**/*.md")
pages = post.render_posts(pages, base_url=base_url)

all_docs = (*posts, *pages)
all_docs = wikilink.annotate_links(all_docs)
all_docs = wikilink.render_wikilinks(all_docs, base_url)

# Collect all docs in memory, so we can iterate over them > once.
all_docs = tuple(all_docs)

taxonomy_index = taxonomy.index_by_taxonomy(all_docs, keys=("tags",))

sitemap_doc = sitemap.gen_sitemap(all_docs, base_url)

posts_rss_doc = rss.create_rss_feed(
    posts,
    base_url=base_url,
    title=site_title + " — latest posts",
    description=site_description,
    author=site_author,
    output_path="posts.xml",
)

all_docs = (sitemap_doc, posts_rss_doc, *all_docs)

id_path_index = {doc.id_path: doc for doc in all_docs}

index = {
    "taxonomy": taxonomy_index,
    "id_path": id_path_index
}

# Set up template globals
context = {
    "rss_docs": (posts_rss_doc,),
    "index": index,
    "site": {
        "title": site_title,
        "description": site_description,
        "author": site_author
    },
    "data": template_data,
    "base_url": base_url
}

all_docs = jinjatools.render(all_docs, theme_path, context=context)

docs.write(all_docs, output_path=output_path)
file.copy_dirs(static_paths, output_path)

print("Done!")