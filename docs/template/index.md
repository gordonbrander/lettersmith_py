----
title: Templates
----

## Plugin

Templates are added to docs with the `lettersmith.templatetools.map_templates` plugin:

```python
docs = templatetools.map_templates(docs)
```

This adds a tuple of templates at `templates` key. The tuple is based on properties of the doc.