The `lettersmith.templatetools.map_template` plugin adds a tuple of templates to each doc. The list is based on the properties of the doc, and goes from most-specific to least-specific. These templates are searched for in order, until an existing template is found.

By default, templates are searched for in this order:

1. `section/SECTION_NAME/single.html` OR `section/SECTION_NAME/index.html` OR `section/SECTION_NAME/list.html`, depending on the type of the doc (single, index, or list)
2. `section/SECTION_NAME/default.html`
3. `single.html` OR `index.html` OR `list.html`, depending on the type of the doc (single, index, or list).
4. `section/default.html`

Of course, you can modify or add to the templates list, using plugins.

## What is a section?

The section is read from the `doc["section"]` of the document (if any). By default, a doc's section is the top-level directory (relative) in its `simple_path`, but of course, you can change this using plugins.

See [[docs]] page for more detail on document items.

## Specifying a template by hand

If you specify a template for a doc with the `doc["meta"]["template"]` key, that template will be added to the front of the list (preferred above all).