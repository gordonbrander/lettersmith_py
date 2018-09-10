#!/usr/bin/env python3
from datetime import datetime
from pathlib import PurePath, Path
from itertools import chain
from subprocess import CalledProcessError
import tempfile

from lettersmith.util import get_deep, tap_each, replace
from lettersmith.argparser import lettersmith_argparser
from lettersmith import path as pathtools
from lettersmith import docs as Docs
from lettersmith import doc as Doc
from lettersmith import stub as Stub
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

    # Grab all markdown files
    paths = input_path.glob("**/*.md")
    # Filter out drafts
    paths = (x for x in paths if pathtools.should_pub(x, build_drafts))
    # Filter out special files
    paths = (x for x in paths if pathtools.is_doc_file(x))

    # Load doc datastructures
    docs = (Doc.load(path, relative_to=input_path) for path in paths)

    # Create a temporary directory for cache.
    with tempfile.TemporaryDirectory(prefix="lettersmith_") as tmp_dir_path:
        cache = Doc.Cache(tmp_dir_path)

        # Process docs one-by-one... render content, etc.
        # TODO we should break mapping functions into single doc
        # processing functions, so we can use Pool.map.
        docs = (wikilink.uplift_wikilinks(doc) for doc in docs)
        docs = (markdowntools.render_doc(doc) for doc in docs)
        docs = (absolutize.absolutize_doc_urls(doc, base_url) for doc in docs)
        docs = (Doc.change_ext(doc, ".html") for doc in docs)
        docs = (templatetools.add_templates(doc) for doc in docs)
        docs = (
            permalink.map_doc_permalink(doc, permalink_templates)
            for doc in docs
        )


        # Pickle processed docs in cache
        docs = tap_each(cache.dump, docs)

        # Convert to stubs in memory
        stubs = tuple(Stub.from_doc(doc) for doc in docs)

        # Gen paging groups and then flatten iterable of iterables.
        paging_doc_iters = paging.gen_paging(stubs, paging_config)
        paging_docs = tuple(chain.from_iterable(paging_doc_iters))

        # Gen rss feed docs. Then collect into a tuple, because we'll be going
        # over this iterator more than once.
        RSS_DEFAULTS = {
            "last_build_date": now,
            "base_url": base_url,
            "title": site_title,
            "description": site_description,
            "author": site_author
        }
        rss_docs_iter = rss.gen_rss_feed(stubs, {
            glob: replace(RSS_DEFAULTS, **group_kwargs)
            for glob, group_kwargs
            in rss_config.items()
        })
        rss_docs = tuple(rss_docs_iter)

        sitemap_doc = sitemap.gen_sitemap(stubs, base_url=base_url)

        # Add generated docs to stubs
        gen_docs = paging_docs + rss_docs + (sitemap_doc,)
        gen_stubs = tuple(Stub.from_doc(doc) for doc in gen_docs)

        wikilink_index = wikilink.index_wikilinks(stubs, base_url=base_url)
        backlink_index = wikilink.index_backlinks(stubs)
        taxonomy_index = taxonomy.index_by_taxonomy(stubs, taxonomies)

        # Create dict index for ad-hoc stub access in templates.
        index = {stub.id_path: stub for stub in (stubs + gen_stubs)}

        # The previous doc generator has been exhausted, so load docs from
        # cache again.
        docs = (cache.load(stub) for stub in stubs)
        # Map wikilinks, but only those that exist in wikilink_index.
        docs = wikilink.map_wikilinks(docs, wikilink_index)

        # Chain together all doc iterators
        docs = chain(docs, gen_docs)

        # Set up template globals
        context = {
            "load_cache": cache.load,
            "rss_docs": rss_docs,
            "index": index,
            "taxonomy_index": taxonomy_index,
            "backlink_index": backlink_index,
            "wikilink_index": wikilink_index,
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
