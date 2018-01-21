import random
import itertools

from jinja2 import Environment, FileSystemLoader

from lettersmith import util
from lettersmith import docs as Docs
from lettersmith import doc as Doc
from lettersmith import templatetools
from lettersmith import path as pathtools
from lettersmith.hash import hash_digest


# The dict of filter functions to be available by default in the template.
FILTERS = {
    "sum": sum,
    "len": len,
    "filter": filter,
    "filterfalse": itertools.filterfalse,
    "islice": itertools.islice,
    "choice": random.choice,
    "sample": random.sample,
    "shuffle": random.shuffle,
    "to_url": pathtools.to_url,
    "get": util.get,
    "sort": util.sort,
    "sort_by": util.sort_by,
    "where": util.where,
    "where_not": util.where_not,
    "where_key": util.where_key,
    "where_contains": util.where_contains,
    "remove_index": Docs.remove_index,
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
    try:
        return len(doc["templates"]) > 0
    except KeyError:
        return False


def renderer(env):
    def render(doc):
        jinja_template = env.select_template(doc["templates"])
        rendered = jinja_template.render(doc)
        return util.put(doc, "content", rendered)
    return render


def map_jinja(docs,
    context={}, filters={}, theme_path="theme"):
    """
    Render a list of docs through Jinja templates.
    Returns a generator of rendered docs.
    """
    all_context = util.merge(CONTEXT, context)
    all_filters = util.merge(FILTERS, filters)
    env = create_env(theme_path, filters=all_filters, context=all_context)
    render = renderer(env)
    return (render(doc) for doc in docs if should_template(doc))