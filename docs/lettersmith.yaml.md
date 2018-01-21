`lettersmith.yaml` is a [yaml](http://yaml.org/) file that contains the configuration details for your site.

Note: what goes into this file depends on the static site generator you've built with Lettersmith. You might not even need one. By convention, we try to use the same fields as `lettersmith_site` uses, but it's not required.

If you're using [[lettersmith_site]], these are the fields used:

```yaml
# Site-wide metadata. Keys added will be available under `site` in templates.
site:
  title: "My Website"
  description: "A description"

# The base url used to qualify links in templates.
base_url: "/"

# The directory containing your source files.
input_path: "content"

# The directory where Lettersmith should write built files.
output_path: "public"

# The path to the theme directory. This directory contains template files for
# your site design.
theme_path: "theme/wiki"

# Static files and directories that should be copied to output_path.
# (recursive for directories)
static_paths:
- "static"

# Path to a directory containing additional YAML metadata to add to
# the template.
data_path: "data"

# Should Lettersmith build drafts? Default is False.
# A draft is any file prefixed with an underscore (_)
build_drafts: False

# Headmatter keys that should be treated as taxonomies
taxonomies:
- tag

# Settings for pagination
# paging:
#   # How many list items per page?
#   per_page: 10
#   # The template used to generate output paths for paging
#   template: "page.html"
#   # The template used to create an output_path.
#   output_path_template: "page/{n}/index.html"
```