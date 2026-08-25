import importlib.metadata

project = "gcip2"
release = version = importlib.metadata.version("gcip2")
html_title = f"{project} {release}"
author = "Arsenii Nikulin"
copyright = "2026, PivLab Dev"

html_theme = "furo"
html_static_path = ["_static"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "myst_parser",
    "sphinx_copybutton",
]

autosectionlabel_prefix_document = True
exclude_patterns = ["_build", "out", "Thumbs.db", ".DS_Store"]
myst_enable_extensions = ["colon_fence"]
viewcode_line_numbers = True

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autoclass_content = "both"
autodoc_preserve_defaults = True
autodoc_default_options = {
    "members": True,
    "private-members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "exclude-members": "model_config, model_fields, model_computed_fields, _abc_impl",
}

# ``Param.type`` and ``BaseInput.type`` are both documented attributes named
# ``type``, so annotations referring to the builtin resolve ambiguously.
suppress_warnings = ["ref.python"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
    "injector": ("https://injector.readthedocs.io/en/latest", None),
    "click": ("https://click.palletsprojects.com/en/stable", None),
}
