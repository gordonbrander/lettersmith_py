import random
import itertools
import json
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from lettersmith import util
from lettersmith import docs as Docs
from lettersmith import doc as Doc
from lettersmith import templatetools
from lettersmith import path as pathtools
from lettersmith.markdowntools import house_markdown
from lettersmith import taxonomy


def _choice(iterable):
    return random.choice(tuple(iterable))


def _shuffle(iterable):
    """
    Shuffles the elements in an iterable, returning a new list.

    Will collect any iterable before sampling.
    This prevents annoying in-template errors, where collecting
    an iterator into a tuple can be non-trivial.
    """
    t = tuple(iterable)
    return random.sample(t, k=len(t))


def _sample(iterable, k):
    """
    Will collect any iterable before sampling.
    This prevents annoying in-template errors, where collecting
    an iterator into a tuple can be non-trivial.
    """
    l = list(iterable)
    try:
        return random.sample(l, k)
    except ValueError:
        return l


def permalink(base_url):
    def permalink_bound(output_path):
        return to_url(output_path, base_url)
    return permalink_bound


class FileSystemEnvironment(Environment):
    def __init__(self, templates_path, filters={}, context={}):
        loader = FileSystemLoader(templates_path)
        super().__init__(loader=loader)
        self.filters.update(filters)
        self.globals.update(context)


TEMPLATE_FUNCTIONS = {
    "markdown": house_markdown,
    "sorted": sorted,
    "json_dumps": json.dumps,
    "sum": sum,
    "len": len,
    "filter": filter,
    "filterfalse": itertools.filterfalse,
    "islice": itertools.islice,
    "choice": _choice,
    "sample": _sample,
    "shuffle": _shuffle,
    "to_url": pathtools.to_url,
    "get": util.get,
    "sorted": sorted,
    "sort_by": util.sort_by,
    "sort_by_len": util.sort_by_len,
    "sort_by_keys": util.sort_by_keys,
    "sort_items_by_key": util.sort_items_by_key,
    "where": util.where,
    "where_not": util.where_not,
    "where_gt": util.where_gt,
    "where_lt": util.where_lt,
    "where_len": util.where_len,
    "where_len_gt": util.where_len_gt,
    "where_len_lt": util.where_len_lt,
    "where_in": util.where_in,
    "where_not_in": util.where_not_in,
    "where_any_in": util.where_any_in,
    "where_matches": util.where_matches,
    "join": util.join,
    "remove_index": Docs.remove_index,
    "remove_id_path": Docs.remove_id_path,
    "filter_siblings": Docs.filter_siblings,
    "to_slug": pathtools.to_slug,
    "to_slugs": util.mapping(pathtools.to_slug),
    "tuple": tuple,
    "json_dumps": json.dumps
}


class LettersmithEnvironment(FileSystemEnvironment):
    """
    Specialized version of default Jinja environment class that
    offers additional filters and environment variables.
    """
    def __init__(self, templates_path, filters={}, context={}):
        loader = FileSystemLoader(templates_path)
        super().__init__(
            templates_path,
            filters=TEMPLATE_FUNCTIONS,
            context=TEMPLATE_FUNCTIONS
        )
        now = datetime.now()
        self.filters.update(filters)
        self.globals.update({"now": now})
        self.globals.update(context)


def should_template(doc):
    """
    Check if a doc should be templated. Returns a bool.
    """
    return len(doc.templates) > 0


def doc_renderer(env):
    """
    Create a render function with a bound environment.
    Returns a render function that can render docs.
    """
    def render_doc(doc):
        """
        Render a document with this Jinja environment.
        """
        if should_template(doc):
            template = env.select_template(doc.templates)
            rendered = template.render({"doc": doc})
            return doc._replace(content=rendered)
        else:
            return doc
    return render_doc


def render(docs, templates_path="theme", context={}, filters={}):
    """
    Wraps up the gory details of creating a Jinja renderer.
    Returns a render function that takes a doc and returns a rendered doc.
    Template comes preloaded with Jinja default filters, and
    Lettersmith default filters and globals.
    """
    render = doc_renderer(LettersmithEnvironment(
        templates_path,
        filters=filters,
        context=context
    ))
    for doc in docs:
        yield render(doc)