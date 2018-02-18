#!/usr/bin/env python3
import tempfile
from datetime import datetime
from pathlib import PurePath, Path
from itertools import chain
from subprocess import CalledProcessError

from lettersmith.argparser import lettersmith_argparser, read_config
from lettersmith import path as pathtools
from lettersmith import docs as Docs
from lettersmith import doc as Doc
from lettersmith import markdowntools
from lettersmith import wikilink
from lettersmith import absolutize
from lettersmith.permalink import map_permalink
from lettersmith import templatetools
from lettersmith import paging
from lettersmith import taxonomy
from lettersmith import jinjatools
from lettersmith import jsontools
from lettersmith import iterstore
from lettersmith.data import load_data_files
from lettersmith.file import copy_all


def main():
    parser = lettersmith_argparser(
        description="""Generates a blog-aware site with Lettersmith""")
    args = parser.parse_args()
    config = read_config(args.config)
    input_path = Path(config["input_path"])
    output_path = config["output_path"]
    theme_path = config["theme_path"]
    base_url = config["base_url"]
    build_drafts = config["build_drafts"]

    with tempfile.TemporaryDirectory(suffix="_lettersmith") as cache_path:
        data = load_data_files(config["data_path"])

        json_paths = (
            x for x in input_path.glob("**/*.json")
            if pathtools.should_pub(x, build_drafts))

        json_docs = Docs.load_json(json_paths, relative_to=input_path)

        yaml_paths = (
            x for x in input_path.glob("**/*.yaml")
            if pathtools.should_pub(x, build_drafts))

        yaml_docs = Docs.load_yaml(yaml_paths, relative_to=input_path)

        md_paths = (
            x for x in input_path.glob("**/*.md")
            if pathtools.should_pub(x, build_drafts))

        md_docs = Docs.load(md_paths, relative_to=input_path)
        md_docs = (wikilink.uplift_wikilinks(doc) for doc in md_docs)
        md_docs = markdowntools.map_markdown(md_docs)
        md_docs = absolutize.map_absolutize(md_docs, base=base_url)

        docs = chain(md_docs, json_docs, yaml_docs)

        docs = (Doc.change_ext(doc, ".html") for doc in docs)
        docs = (Doc.decorate_smart_items(doc) for doc in docs)
        docs = templatetools.map_templates(docs)
        docs = map_permalink(docs, config["permalink_templates"])

        doc_cache_path = PurePath(cache_path, "docs.txt")
        # Store current state of docs to disk.
        # Class instance is an iterable that will read them back out from disk.
        # This allows you to consume the iterator more than once.
        docs_store = iterstore.store(docs, doc_cache_path)

        stub_docs = tuple(Doc.rm_content(doc) for doc in docs_store)

        index = Docs.reduce_index(stub_docs)
        wikilink_index = wikilink.index_wikilinks(stub_docs, base=base_url)
        backlink_index = wikilink.index_backlinks(stub_docs)
        taxonomy_index = taxonomy.index_by_taxonomy(
            stub_docs, config["taxonomies"])

        paging_docs = paging.gen_paging(stub_docs, **config["paging"])

        docs = wikilink.map_wikilinks(docs_store, wikilink_index)
        docs = (Doc.decorate_summary(doc) for doc in docs)

        docs = chain(docs, paging_docs)

        # Set up template globals
        context = {
            "index": index,
            "taxonomy_index": taxonomy_index,
            "backlink_index": backlink_index,
            "wikilink_index": wikilink_index,
            "site": config["site"],
            "data": data,
            "base_url": base_url,
            "now": datetime.now()
        }

        docs = jinjatools.map_jinja(
            docs, context=context, theme_path=theme_path)
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