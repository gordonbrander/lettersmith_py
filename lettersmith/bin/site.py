#!/usr/bin/env python3
from datetime import datetime
from pathlib import PurePath, Path
from itertools import chain
from subprocess import CalledProcessError

from lettersmith.argparser import lettersmith_argparser
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
from lettersmith.data import load_data_files
from lettersmith.file import copy, copy_all


def main():
    parser = lettersmith_argparser(
        description="""Generates a blog-aware site with Lettersmith""")
    args = parser.parse_args()
    config = args.config
    theme_path = config.get("theme_path", "theme")
    input_path = config.get("input_path", "content")
    output_path = config.get("output_path", "public")
    data_path = config.get("data_path", "data")
    static_paths = config.get("static_paths", [])
    base_url = config.get("base_url", "/")
    build_drafts = config.get("build_drafts", False)
    permalink_templates = config.get("permalink_templates", {})
    taxonomies = config.get("taxonomies")
    site = config.get("site", {})

    data = load_data_files(data_path)

    md_paths = tuple(Path(input_path).glob("**/*.md"))
    docs = Docs.load(md_paths, relative_to=input_path)
    docs = docs if build_drafts else Docs.remove_drafts(docs)

    docs = (Doc.decorate_smart_items(doc) for doc in docs)
    docs = templatetools.map_templates(docs)
    docs = (wikilink.uplift_wikilinks(doc) for doc in docs)
    docs = map_permalink(docs, permalink_templates)

    # Remove content field...
    docs = (Doc.rm_content(doc) for doc in docs)
    # ...then collect docs into memory.
    # Now we do all our cross-referencing.
    # Doing this little dance increases the upper limit on the number
    # of files that can be processed — particularly for sites with
    # extremely large numbers of large docs.
    docs = tuple(docs)

    wikilink_index = wikilink.index_wikilinks(docs, base=base_url)
    backlink_index = wikilink.index_backlinks(docs)

    # Create doc index dict for template
    index = Docs.reduce_index(docs)
    taxonomy_index = taxonomy.index_by_taxonomy(docs, taxonomies=taxonomies)

    paging_docs = paging.gen_paging(docs, **paging.read_config(config))

    # Bring back content field (in generator, so only one content is
    # in memory at a time).
    docs = (Doc.reload_content(doc) for doc in docs)
    docs = wikilink.map_wikilinks(docs,
        wikilink_index=wikilink_index, base=base_url)
    docs = markdowntools.map_markdown(docs)
    docs = absolutize.map_absolutize(docs, base=base_url)

    docs = chain(docs, paging_docs)

    # Set up template globals
    context = {
        "index": index,
        "taxonomy_index": taxonomy_index,
        "backlink_index": backlink_index,
        "site": site,
        "data": data,
        "base_url": base_url,
        "now": datetime.now()
    }

    docs = jinjatools.map_jinja(docs, context=context, theme_path=theme_path)

    # Copy static files from project dir (if any)
    try:
        copy_all(static_paths, output_path)
    except CalledProcessError:
        pass

    # Copy static files from theme (if any)
    try:
        copy(PurePath(theme_path, "static"), output_path)
    except CalledProcessError:
        pass

    stats = Docs.write(docs, output_path=output_path)

    print('Done! Generated {sum} files in "{output_path}"'.format(
        output_path=output_path,
        sum=stats["written"]
    ))


if __name__ == "__main__":
    main()