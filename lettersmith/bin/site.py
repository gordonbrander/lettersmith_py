#!/usr/bin/env python3
from datetime import datetime
from pathlib import PurePath, Path
from itertools import chain
from subprocess import CalledProcessError

from lettersmith.util import get_deep, replace
from lettersmith.argparser import lettersmith_argparser
from lettersmith import path as pathtools
from lettersmith import docs as Docs
from lettersmith import doc as Doc
from lettersmith import markdowntools
from lettersmith import wikilink
from lettersmith import absolutize
from lettersmith import permalink
from lettersmith import templatetools
from lettersmith import paging
from lettersmith import taxonomy
from lettersmith import jinjatools
from lettersmith import rss
from lettersmith import sitemap
from lettersmith.data import load_data_files
from lettersmith.file import copy_all


def main():
    parser = lettersmith_argparser(
        description="""Generates a blog-aware site with Lettersmith""")
    args = parser.parse_args()
    config = args.config
    input_path = Path(config.get("input_path", "content"))
    output_path = config.get("output_path", "public")
    theme_path = config.get("theme_path", "theme")
    base_url = config.get("base_url", "/")
    build_drafts = config.get("build_drafts", False)
    data_path = config.get("data_path", "data")
    static_paths = config.get("static_paths", [])
    permalink_templates = config.get("permalink_templates", {})
    rss_config = config.get("rss", {"*": {"output_path": "feed.rss"}})
    paging_config = config.get("paging", {})
    taxonomies = get_deep(config, ("taxonomies", "keys"), tuple())
    taxonomy_output_path_template = get_deep(config,
        ("taxonomy", "output_path_template"))
    site_title = get_deep(config, ("site", "title"), "Untitled")
    site_description = get_deep(config, ("site", "description"), "")
    site_author = get_deep(config, ("site", "author"), "")
    now = datetime.now()

    data = load_data_files(data_path)

    # Grab all markdown, YAML, and JSON files.
    md_paths = input_path.glob("**/*.md")
    md_paths = (x for x in md_paths if pathtools.should_pub(x, build_drafts))
    md_docs = (Doc.load(path, relative_to=input_path) for path in md_paths)
    md_docs = (markdowntools.render_doc(doc) for doc in md_docs)

    yaml_paths = input_path.glob("**/*.yaml")
    yaml_paths = (x for x in yaml_paths if pathtools.should_pub(x, build_drafts))
    yaml_docs = (Doc.load(path, relative_to=input_path) for path in yaml_paths)
    yaml_docs = (Doc.parse_yaml(doc) for doc in yaml_docs)

    json_paths = input_path.glob("**/*.json")
    json_paths = (x for x in json_paths if pathtools.should_pub(x, build_drafts))
    json_docs = (Doc.load(path, relative_to=input_path) for path in json_paths)
    json_docs = (Doc.parse_json(doc) for doc in json_docs)

    docs = chain(md_docs, yaml_docs, json_docs)

    absolutize_doc_urls = absolutize.absolutize(base_url)
    docs = (absolutize_doc_urls(doc) for doc in docs)
    docs = (Doc.change_ext(doc, ".html") for doc in docs)
    docs = (templatetools.add_templates(doc) for doc in docs)
    docs = (
        permalink.map_doc_permalink(doc, permalink_templates)
        for doc in docs
    )
    docs = wikilink.annotate_links(docs)
    docs = wikilink.render_wikilinks(docs, base_url)

    # Collect all docs in memory, so we can consume them > once.
    docs = tuple(docs)

    # Generate paging docs
    paging_docs = tuple(paging.gen_paging(docs, paging_config))

    rss_docs = tuple(rss.gen_rss_feed(
        docs,
        rss_config,
        last_build_date=now,
        base_url=base_url,
        author=site_author
    ))

    sitemap_doc = sitemap.gen_sitemap(docs, base_url=base_url)

    gen_docs = paging_docs + rss_docs + (sitemap_doc,)

    index = {}
    index["taxonomy"] = taxonomy.index_by_taxonomy(docs, taxonomies)

    docs = docs + gen_docs

    index["id_path"] = {
        doc.id_path: doc
        for doc in docs
    }

    # Set up template globals
    context = {
        "rss_docs": rss_docs,
        "index": index,
        "site": config.get("site", {}),
        "data": data,
        "base_url": base_url,
        "now": now
    }


    # Create a render function
    render_jinja = jinjatools.lettersmith_doc_renderer(
        theme_path,
        context=context
    )
    docs = (render_jinja(doc) for doc in docs)

    stats = Docs.write(docs, output_path=output_path)

    try:
        static_paths = config.get("static_paths", [])
        static_paths.append(PurePath(theme_path, "static"))
        copy_all(static_paths, output_path)
    except CalledProcessError:
        pass

    print('Done! Generated {sum} files in "{output_path}"'.format(
        output_path=output_path,
        sum=stats["written"]
    ))


if __name__ == "__main__":
    main()
