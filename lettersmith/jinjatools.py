import random
import itertools
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from lettersmith import util
from lettersmith import docs as Docs
from lettersmith import doc as Doc
from lettersmith import query
from lettersmith.lens import get, put
from lettersmith import path as pathtools
from lettersmith.markdowntools import markdown


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


def _permalink(base_url):
    def permalink_bound(output_path):
        return pathtools.to_url(output_path, base_url)
    return permalink_bound


class FileSystemEnvironment(Environment):
    def __init__(self, templates_path, filters={}, context={}):
        loader = FileSystemLoader(templates_path)
        super().__init__(loader=loader)
        self.filters.update(filters)
        self.globals.update(context)


TEMPLATE_FUNCTIONS = {
    "sorted": sorted,
    "len": len,
    "islice": itertools.islice,
    "choice": _choice,
    "sample": _sample,
    "shuffle": _shuffle,
    "to_url": pathtools.to_url,
    "join": util.join,
    "tuple": tuple
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
        self.filters.update(filters)
        self.globals.update(context)


def should_template(doc):
    """
    Check if a doc should be templated. Returns a bool.
    """
    return get(Doc.template, doc) is not ""


def jinja(templates_path, base_url, context={}, filters={}):
    """
    Wraps up the gory details of creating a Jinja renderer.
    Returns a render function that takes a doc and returns a rendered doc.
    Template comes preloaded with Jinja default filters, and
    Lettersmith default filters and globals.
    """
    now = datetime.now()
    env = LettersmithEnvironment(
        templates_path,
        filters={"permalink": _permalink(base_url), **filters},
        context={"now": now, **context}
    )

    @query.maps
    @Doc.annotate_exceptions
    def render(doc):
        if should_template(doc):
            template = env.get_template(doc.template)
            rendered = template.render({"doc": doc})
            return put(Doc.content, doc, rendered)
        else:
            return doc

    return render