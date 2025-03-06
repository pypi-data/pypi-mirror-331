![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

# MkDocs author plugin

Manually define authors in your markdown files and render a GitHub avatar
at the bottom of the page.

> [!NOTE]
> This plugin was specifically written for use with Material for MkDocs.

## Get started

Install the package with:

```bash
pip install mkdocs-author-plugin
```

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - author:
    authors_file: authors.yml
```

Place the `authors.yml` within the `docs` directory. `authors.yml` contains all
authors with their GitHub usernames:

```yaml
jk:  # author key
  name: Jakob Klotz
  github: JakobKlotz  # GitHub username

john_doe:
  name: John Doe
  github: johndoe
```

Within your markdown files, define the authors using their keys in the 
front matter:

```markdown
---
title: My Markdown Page
authors:
  - jk
  - john_doe
---

....

```
