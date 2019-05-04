# Lettersmith

A set of tools for static site generation. It comes with a static site generator bundled in. You can also use it as a library to build your own custom static site generator.

I built it for myself, because I found other solutions to be pretty baroque and difficult to customize. Right now, it's a simple set of fairly stable tools for personal use. I might package it up later.

## Installing

Lettersmith requires Python 3+, and a version of pip compatible with Python 3.

```bash
git clone https://github.com/gordonbrander/lettersmith_py
cd lettersmith_py
pip3 install -e .
```

## lettersmith_site

Lettersmith comes bundled with a static site generator `lettersmith_site` that can do most of what Jekyll, et al do.

`lettersmith_site` takes a single argument — a path to a yaml config file.

```bash
lettersmith_site lettersmith.yaml
```

## lettersmith_scaffold

You can easily scaffold a site using `lettersmith_scaffold`.

```bash
lettersmith_scaffold . --type wiki
```

This will plop a yaml config file and a theme directory you can customize into your project directory. Right now there is just one type: "wiki", though I hope to add more for common site types (e.g. blog, portfolio, etc).

## What it does

Lettersmith comes bundled with a static site generator, but it's really just a library of tools for transforming text. You can use these tools to create your own custom static site generators, build tools, project scaffolders, ebook generators, or wikis — whatever you like.

Lettersmith loads text files as Python namedtuples, so a markdown file like this:

```markdown
---
title: "My post"
date: 2018-01-17
---

Some content
```

Becomes this:

```python
Doc(
  id_path='path/to/post.md',
  output_path='path/to/post/index.html',
  input_path='content/path/to/post.md',
  created=datetime.datetime(2018, 12, 31, 16, 0),
  modified=datetime.datetime(2018, 12, 31, 16, 0),
  title='My post',
  content='Some content',
  section='path',
  meta={
    "title": "My post",
    "date": "2018-12-31"
  },
  templates=()
)
```

## Plugins

Plugins are just functions that transform namedtuples.

To transform many files, you can load them into an iterable, then use list comprehensions, generator expressions, and map, filter, reduce:

```python
# Get all markdown paths under source/
paths = Path("source").glob("*.md")
# Load them as doc namedtuples
docs = Docs.load(paths)
# Transform them with your function.
docs = my_plugin(docs)
```

"Plugins" are just generator functions that take an iterator of docs and
yield transformed docs.

```python
def my_plugin(docs)
    for doc in docs:
        yield do_something(doc)
```

When you're done transforming things, you can pass the iterable to `Docs.write`, which takes care of writing out the files to an output directory.

```python
Docs.write(docs, output_path=output_path)
```

That's it!

Lettersmith comes with a swiss army knife of helpful tools for things like Markdown, templates, drafts, tags, wikilinks, and more — and if you see something missing it's easy to write your own functions.