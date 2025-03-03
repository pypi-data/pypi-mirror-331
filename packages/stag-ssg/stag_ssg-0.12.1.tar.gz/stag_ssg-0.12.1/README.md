# Stag

<p align="center">
  <a href="https://git.goral.net.pl/stag">
    <img alt="Logo featuring a stag" src="https://git.goral.net.pl/stag.git/plain/doc/stag.png" width="320"/>
  </a>
</p>

Stag is a simple, extensible static site generator, where almost every part
is a plug in. It's almost too easy to extend it with your own
functionalities.

- [Online documentation](https://pages.goral.net.pl/stag)
- [Main repository](https://git.goral.net.pl/stag.git)

## Features

Out of the box Stag comes with the following features:

- pages can be generated from Markdown with enabled support for footnotes,
  fenced code blocks and some typographic goodies.
- support for Asciidoc (via asciidoctor)
- generic support for file front matters
- Jinja2 templates
- taxonomies (e.g. tags)
- RSS feeds
- generation of nice URLs:
  - _foo/index.md_ → _foo/index.html_
  - _bar.md_ → _bar/index.html_
- extensible with plugins and macros (shortcodes)

## Installation

PyPI: https://pypi.org/project/stag-ssg/

## Issues

[Issue Tracker](https://issues.goral.net.pl/public/board/fabf36e2ca2bc4d768fe7e7d401cc86a650178268ded7efd5e27ee46b6ed)

Please report new issues to dev@goral.net.pl.
