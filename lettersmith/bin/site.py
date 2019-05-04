#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import PurePath, Path
from itertools import chain
from voluptuous import Optional
from lettersmith import config
from lettersmith import path as pathtools
from lettersmith import docs as Docs
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
from lettersmith.file import copy_dirs


parser = argparse.ArgumentParser(
    description="""Generates a blog-aware site with Lettersmith"""
)
parser = config.add_config_argument(parser)


# Extend the basic configuration schema with config schemas for plugins.
schema = config.schema.extend({
    Optional("paging", default={}): paging.schema,
    Optional("taxonomy", default={}): taxonomy.schema,
    Optional("permalink", default={}): permalink.schema,
    Optional("paging", default={}): paging.schema,
    Optional("rss", default={}): rss.schema
})


def main():
    args = parser.parse_args()
    config = schema(args.config)
    input_path = Path(config["input_path"])
    now = datetime.now()

    data = load_data_files(config["data_path"])

    # Grab all markdown, YAML, and JSON files.
    md_paths = input_path.glob("**/*.md")
    md_paths = (x for x in md_paths if pathtools.should_pub(x, config["build_drafts"]))
    md_docs = Docs.load(md_paths, relative_to=input_path)
    md_docs = markdowntools.parse_markdown(md_docs)

    yaml_paths = input_path.glob("**/*.yaml")
    yaml_paths = (x for x in yaml_paths if pathtools.should_pub(x, config["build_drafts"]))
    yaml_docs = Docs.load(yaml_paths, relative_to=input_path)
    yaml_docs = Docs.parse_yaml(yaml_docs)

    json_paths = input_path.glob("**/*.json")
    json_paths = (x for x in json_paths if pathtools.should_pub(x, config["build_drafts"]))
    json_docs = Docs.load(json_paths, relative_to=input_path)
    json_docs = Docs.parse_json(json_docs)

    docs = chain(md_docs, yaml_docs, json_docs)

    docs = absolutize.absolutize(docs, config["base_url"])
    docs = Docs.change_ext(docs, ".html")
    docs = templatetools.add_templates(docs)
    docs = permalink.replace_permalinks(docs, **config["permalink"])
    docs = wikilink.annotate_links(docs)
    docs = wikilink.render_wikilinks(docs, config["base_url"])

    # Collect all docs in memory, so we can consume them > once.
    docs = tuple(docs)

    taxonomy_index = taxonomy.index_by_taxonomy(docs, config["taxonomy"]["keys"])

    sitemap_doc = sitemap.gen_sitemap(docs, config["base_url"])
    paging_docs = paging.paging(docs, **config["paging"])
    rss_docs = rss.gen_rss_feed(docs, config["base_url"], **config["rss"])

    docs = docs + (sitemap_doc, *paging_docs, *rss_docs)

    id_path_index = {
        doc.id_path: doc
        for doc in docs
    }

    index = {
        "taxonomy": taxonomy_index,
        "id_path": id_path_index
    }

    # Set up template globals
    context = {
        "rss_docs": rss_docs,
        "index": index,
        "site": config["site"],
        "data": data,
        "base_url": config["base_url"],
        "now": now
    }

    # Render doc templates with Jinja
    docs = jinjatools.render(docs, config["theme_path"], context=context)

    stats = Docs.write(docs, output_path=config["output_path"])

    # Copy static files
    theme_static_path = PurePath(config["theme_path"], "static")
    static_dirs = (theme_static_path, *config["static_paths"])
    copy_dirs(static_dirs, config["output_path"])

    print('Done! Generated {sum} files in "{output_path}"'.format(
        output_path=config["output_path"],
        sum=stats["written"]
    ))


if __name__ == "__main__":
    main()
