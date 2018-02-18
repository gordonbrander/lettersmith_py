A typical doc has these properties.

```python
{
  # Read from doc["meta"]["title"] or generated from file name
  "title": "...",
  # The content of the file (usually the stuff below headmatter)
  "content": "...",
  # A datetime representing last time file was modified
  "modified_time": datetime,
  # A datetime representing when file was created
  "created_time": datetime,
  # A datetime representing date in headmatter.
  # Falls back to created_time.
  "date": datetime,
  # A datetime representing modified key in headmatter.
  # Falls back to modified_time.
  "modified": datetime,
  # A tuple of templates associated with this content.
  # This will frontload doc["meta"]["template"], if it is present.
  # The first template that exists will be used.
  "templates": ("...", "..."),
  # The source file path for this file. Generated docs don't have this field.
  "input_path": "x/y/z.md",
  # The "simple" path before being transformed for permalinks.
  # For docs that have a source on the filesystem this is the same
  # as the input path. For generated docs, this is whatever makes
  # sense. Used to infer information about the doc, such as what
  # directory it belongs to.
  "id_path": "x/y/z.md",
  # The path this doc will be written to. Often transformed via permalink
  # plugin.
  "output_path": "x/y/z/index.html",
  # Typically, the tld of id_path. Useful for having different
  # templates for different sections of your website.
  "section": "",
  # Contains the parsed values of everything in the headmatter.
  "meta": {
    "my_custom_prop": True
  }
}
```

Plugins can add and remove properties. If you're a plugin author, the convention is to check your key access, either with try/catch, or via `dict.get` or `lettersmith.util.get`.