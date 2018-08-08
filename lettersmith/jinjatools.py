import random
import itertools

from jinja2 import Environment, FileSystemLoader

from lettersmith import util
from lettersmith import docs as Docs
from lettersmith import doc as Doc
from lettersmith import templatetools
from lettersmith import path as pathtools
from lettersmith.hash import hash_digest
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


# The dict of filter functions to be available by default in the template.
FILTERS = {
    "markdown": house_markdown,
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
    "sort": util.sort,
    "sort_by": util.sort_by,
    "where": util.where,
    "where_key": util.where_key,
    "where_not_key": util.where_not_key,
    "where_contains": util.where_contains,
    "where_matches": util.where_matches,
    "where_taxonomy_contains_any": taxonomy.where_taxonomy_contains_any,
    "remove_index": Docs.remove_index,
    "remove_id_path": Docs.remove_id_path,
    "filter_siblings": Docs.filter_siblings,
    "hash_digest": hash_digest
}

# A dict of globals available by default in the template
CONTEXT = {
    "get": util.get,
    "len": len,
    "sum": sum
}


def create_env(templates_path, filters={}, context={}):
    """
    Factory. Create Jinja environment and populate it with filters.
    `templates_path` is a pathlike that points to the the template directory.
    `filters` is a dict of functions to be added to environment.
    """
    env = Environment(loader=FileSystemLoader(templates_path))
    env.filters.update(filters)
    env.globals.update(context)
    return env


def should_template(doc):
    """
    Check if a doc should be templated. Returns a bool.
    """
    return len(doc.templates) > 0


def renderer(env):
    """
    Create a render function with a bound environment.
    Returns a render function.
    """
    def render(doc):
        """
        Render a document with bound environment.
        """
        jinja_template = env.select_template(doc.templates)
        rendered = jinja_template.render({"doc": doc})
        return util.replace(doc, content=rendered)
    return render


def map_jinja(docs, context={}, filters={}, theme_path="theme"):
    """
    Render a list of docs through Jinja templates.
    Returns a generator of rendered docs.
    """
    all_context = util.merge(CONTEXT, context)
    all_filters = util.merge(FILTERS, filters)
    env = create_env(theme_path, filters=all_filters, context=all_context)
    render = renderer(env)
    return util.map_match(should_template, render, docs)
