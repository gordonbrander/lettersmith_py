import random
import itertools

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


class LettersmithEnvironment(FileSystemEnvironment):
    """
    Specialized version of default Jinja environment class that
    offers additional filters and environment variables.
    """
    lettersmith_filters = {
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
        "join": util.join,
        "where_taxonomy_contains_any": taxonomy.where_taxonomy_contains_any,
        "remove_index": Docs.remove_index,
        "remove_id_path": Docs.remove_id_path,
        "filter_siblings": Docs.filter_siblings,
        "to_slug": pathtools.to_slug,
        "to_slugs": util.lift_iter(pathtools.to_slug),
        "tuple": tuple
    }

    lettersmith_globals = {
        "get": util.get,
        "len": len,
        "sum": sum
    }

    def __init__(self, templates_path, filters={}, context={}):
        loader = FileSystemLoader(templates_path)
        super().__init__(templates_path, filters=filters, context=context)
        self.filters.update(self.lettersmith_filters)
        self.globals.update(self.lettersmith_globals)


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
            return util.replace(doc, content=rendered)
        else:
            return doc
    return render_doc


def lettersmith_doc_renderer(templates_path="theme", context={}, filters={}):
    """
    Wraps up the gory details of creating a Jinja renderer.
    Returns a render function that takes a doc and returns a rendered doc.
    Template comes preloaded with Jinja default filters, and
    Lettersmith default filters and globals.
    """
    return doc_renderer(LettersmithEnvironment(
        templates_path,
        filters=filters,
        context=context
    ))