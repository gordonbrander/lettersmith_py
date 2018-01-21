----
title: Templates
----

[[lettersmith_site]] uses [Jinja2](https://jinja.pocoo.org) for templating. Jinja is a popular Python templating language with some useful features like template inheritance.

## TOC

- [[Template Variables]]: what variables are available in templates.
- [[Template Lookup Order]]: what template gets chosen?

## How the template plugins work

Templates are added to docs with the `lettersmith.templatetools.map_templates` plugin:

```python
docs = templatetools.map_templates(docs)
```

This adds a tuple of templates at `templates` key. The tuple is based on properties of the doc. See [[Template Lookup Order]] for more on which templates are added.

After the templates have been added to the doc, [[lettersmith_site]] renders the templates using [Jinja2](https://jinja.pocoo.org).

```python
docs = jinjatools.map_jinja(docs,
  context=context, filters=filters, theme_path=theme_path)
```

If you're writing a custom static site generator, it's worth noting this is typically done last, since it renders the doc contents as a full HTML page, and there's not much you can do with it after that.