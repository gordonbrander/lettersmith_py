`lettersmith_site` is the command for the default static site generator bundled into Lettersmith.

You don't have to use it, (it's a small script and you could easily make your own) but it's convenient and should solve the 80% case.

## How to use it

`lettersmith_site` takes a single argument, a path to a yaml config file, containing the settings for your site.

```bash
lettersmith_site lettersmith.yaml
```

This will build your site and print a confirmation when it's done.

You can name the yaml config file anything, but we usually call it `lettersmith.yaml`, because it's a helpful convention. If you want to keep multiple configurations (for production and development, say), it can be nice to name them something like `lettersmith.prod.yaml`, `lettersmith.dev.yaml`.

See [[lettersmith.yaml]] for more about configuration, and what kind of information goes into this file.