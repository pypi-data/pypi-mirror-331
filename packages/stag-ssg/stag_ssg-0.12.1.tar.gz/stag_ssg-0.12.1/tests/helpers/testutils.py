import markdown

from stag.ecs import Page, Path, Content


def add_named_md_file(site, source_path, url, text, metadata=None, parse=False):
    if metadata is None:
        metadata = {}

    config = site.config
    html = markdown.markdown(text) if parse else None
    return site.make_page(
        url,
        source=Path(source_path, site.config.content),
        metadata=metadata,
        input=Content("md", text),
        output=Content("html", html),
    )


def add_md_file(site, text, metadata=None, parse=False):
    return add_named_md_file(site, "page/index.md", "/page", text, metadata, parse)


def contents(path):
    with open(path) as file:
        return file.read().strip()
