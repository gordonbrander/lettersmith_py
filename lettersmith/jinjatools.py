import random
import itertools
import json
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from lettersmith import util
from lettersmith import docs as Docs
from lettersmith.doc import annotate_exceptions
from lettersmith import path as pathtools
from lettersmith.markdowntools import markdown
from lettersmith import select


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
    "markdown": markdown,
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
    "sorted": sorted,
    "select": select.select,
    "sort": select.sort,
    "where": select.where,
    "attr": select.attr,
    "key": select.key,
    "first": select.first,
    "gt": select.gt,
    "lt": select.lt,
    "eq": select.eq,
    "neq": select.neq,
    "has": select.has,
    "has_any": select.has_any,
    "id_path": select.id_path,
    "output_path": select.output_path,
    "title": select.title,
    "section": select.section,
    "created": select.created,
    "modified": select.modified,
    "meta": select.meta,
    "sort_items_by_key": util.sort_items_by_key,
    "join": util.join,
    "remove_index": Docs.remove_index,
    "remove_id_path": Docs.remove_id_path,
    "filter_siblings": Docs.filter_siblings,
    "to_slug": pathtools.to_slug,
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
    return len(doc.templates) > 0


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

    @annotate_exceptions
    def render_doc(doc):
        if should_template(doc):
            template = env.select_template(doc.templates)
            rendered = template.render({"doc": doc})
            return doc._replace(content=rendered)
        else:
            return doc

    def render(docs):
        """
        Render docs with Jinja templates
        """
        for doc in docs:
            yield render_doc(doc)
    return render