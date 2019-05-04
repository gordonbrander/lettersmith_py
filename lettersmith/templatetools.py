from pathlib import PurePath

from lettersmith import path as pathtools
from lettersmith import util


SECTION_TEMPLATE = "section/{section}/{basename}"


def read_affiliated_templates(pathlike):
    """
    Return a tuple of templates that are related to the given the path.
    Typically used for files read from FS.
    """
    purepath = PurePath(pathlike)
    name = purepath.stem
    section = pathtools.tld(purepath)
    templates = []
    single_basename = "index.html" if name == "index" else "single.html"

    if section != "":
        templates.append(SECTION_TEMPLATE.format(
            section=section,
            basename=single_basename))
        templates.append(SECTION_TEMPLATE.format(
            section=section,
            basename="default.html"))

    templates.append(single_basename)
    templates.append("default.html")

    return templates


def add_doc_templates(doc):
    """
    Read potential templates for doc

    - Grabs any custom template from headmatter
    - Allows you to add additional templates via `templates` kwarg.
    - Reads affiliated "smart" templates based on doc info
    """
    templates = []
    try:
        custom_template = doc.meta["template"]
        templates.insert(0, custom_template)
    except KeyError:
        pass

    # Add some "affiliated" implicit templates... these are templates that
    # are associated with doc attributes.
    affiliated_templates = read_affiliated_templates(doc.id_path)
    templates.extend(affiliated_templates)

    # Carry over any existing templates
    try:
        templates.extend(doc.templates)
    except KeyError:
        pass
    return doc._replace(templates=tuple(templates))


# Plugin version that adds templates to an iterable of docs.
add_templates = util.mapping(add_doc_templates)