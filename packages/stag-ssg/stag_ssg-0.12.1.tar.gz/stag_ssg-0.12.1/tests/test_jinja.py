import os
import pytest

from stag.utils import chdir
from stag.config import TemplateTable
from stag.writers.jinja import render_page, get_env

from testutils import add_named_md_file, contents


@pytest.fixture(autouse=True)
def jinja_config(config):
    config.template = TemplateTable()
    config.template.name = "theme"
    return config


@pytest.fixture(autouse=True)
def default_templates(jinja_config, tmp_path):
    templates_dir = tmp_path / jinja_config.template.name
    templates_dir.mkdir()

    html_templ = templates_dir / "page.html"
    html_content = "<html><body>{{ content }}</body></html>"
    html_templ.write_text(html_content)
    print(html_templ)


# sourcepath shouldn't be important for this test, but we'll test it anyway
@pytest.mark.parametrize(
    "sourcepath", ("page/index.md", "index.md", "page.md", "page/page.md")
)
@pytest.mark.parametrize(
    "url,outpath",
    [
        ("/page", "page/index.html"),
        ("/page.html", "page.html"),
        ("/page/index.html", "page/index.html"),
        ("/page.html", "page.html"),
        ("/page.json", "page.json"),
        ("/page/index.json", "page/index.json"),
    ],
)
def test_render_output(site, tmp_path, sourcepath, url, outpath):
    mdfile = add_named_md_file(site, sourcepath, url, "Content", parse=True)
    render_exp = f"<html><body>{mdfile.output.content}</body></html>"

    with chdir(tmp_path):
        env = get_env(site.config)
        render_page(mdfile, site, env)

        outfile = os.path.join(tmp_path, site.config.output, outpath)
        assert os.path.isfile(outfile)
        assert contents(outfile) == render_exp
