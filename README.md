# Lettersmith

A set of tools for static site generation. It comes with a static site generator bundled in. You can also use it as a library to build your own custom static site generator.

I built it for myself, because I found other solutions to be pretty baroque and difficult to customize. Right now, it's a simple set of fairly stable tools for personal use. I might package it up later.

## Installing

Lettersmith requires Python 3.6+, and a version of pip compatible with Python 3.

```bash
git clone https://github.com/gordonbrander/lettersmith_py
cd lettersmith_py
pip3 install -e .
```

## lettersmith_scaffold

You can easily scaffold a site using `lettersmith_scaffold`.

```bash
lettersmith_scaffold ./blog --type blog
```

This will stub out a directory structure and a build script for a typical blogging setup. You can customize the build script from there.


## What it does

Lettersmith comes bundled with a static site generator, but it's really just a library of tools for transforming text. You can use these tools to create your own custom static site generators, build tools, project scaffolders, ebook generators, or wikis — whatever you like.

Lettersmith loads text files as Python namedtuples, so a markdown file like this:

```markdown
---
title: "My post"
created: 2018-01-17
---

Some content
```

Becomes this:

```python
Doc(
  id_path='path/to/post.md',
  output_path='path/to/post.md',
  input_path='path/to/post.md',
  created=datetime.datetime(2018, 1, 17, 0, 0),
  modified=datetime.datetime(2018, 1, 17, 0, 0),
  title='My post',
  content='Some content',
  meta={
    "title": "My post",
    "date": "2018-01-17"
  },
  template=""
)
```


## Plugins

Plugins are just functions that transform doc namedtuples.

To transform many files, you can load them into an iterable, then use list comprehensions, generator expressions, and map, filter, reduce:

```python
# Get all markdown docs under source/
posts = docs.find("posts/*.md")
# Transform them with your function.
posts = my_plugin(posts)
```

To write a plugin, all you need to do is define a generator function that takes an iterator of docs and yields transformed docs.

```python
def my_plugin(docs)
    for doc in docs:
        yield do_something(doc)
```

You can pipe docs through many transforming functions using `pipe`.

```python
posts = pipe(
  docs.find("source/*.md"),
  markdown.content,
  my_plugin,
  my_other_plugin
)
```

Which is equivalent to:

```python
posts = my_other_plugin(my_plugin(markdown.content(docs.find("source/*.md"))))
```

When you're done transforming things, you can pass the iterable to `write`, which takes care of writing out the files to an output directory.

```python
write(posts, directory="public")
```

That's it!

Check out [blog/build.py](/lettersmith/package_data/scaffold/blog/build.py) for an example of a build script that uses some of the built-in plugins to create a typical blogging setup.

Lettersmith comes with a swiss army knife of helpful tools for things like Markdown, templates, drafts, tags, wikilinks, and more — and if you see something missing it's easy to write your own functions.