`lettersmith_scaffold` lets you quickly stub out new sites by copying a ready-to-go project into an empty project directory.

## How to use it

```bash
lettersmith_scaffold . --type wiki
```

(Note the `.`, which is the path to the directory you want to put your project in.)

This will plop a `.yaml` config file, a theme directory you can customize, and some useful demo content into your project directory.

You can get up-and-running in a single command:

```base
lettersmith_scaffold . && lettersmith_site lettersmith.yaml
```

This will set up a project in the current directory, then build it.

## Site types

the `--type` argument lets you choose from a list of pre-made templates.

Right now there is just one type: "wiki", though I hope to add more for common site types (e.g. blog, portfolio, etc).