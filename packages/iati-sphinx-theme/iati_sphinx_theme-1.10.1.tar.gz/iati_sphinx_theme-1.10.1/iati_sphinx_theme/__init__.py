"""A sphinx theme for IATI documentation sites."""

from datetime import datetime
from os import path

import sphinx.application


def setup(app: sphinx.application.Sphinx) -> None:
    app.add_html_theme("iati_sphinx_theme", path.abspath(path.dirname(__file__)))
    app.config["html_permalinks_icon"] = "#"
    app.config["html_favicon"] = "static/favicon-16x16.png"
    app.config["html_context"]["language"] = app.config["language"]
    app.config["html_context"]["current_year"] = datetime.now().year
    app.add_js_file("language-switcher.js")
    locale_path = path.join(path.abspath(path.dirname(__file__)), "locale")
    app.add_message_catalog("sphinx", locale_path)
