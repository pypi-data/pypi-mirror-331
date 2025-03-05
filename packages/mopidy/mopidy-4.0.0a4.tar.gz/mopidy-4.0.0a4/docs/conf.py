"""Mopidy documentation build configuration file"""

import os
from importlib.metadata import version

# -- Custom Sphinx setup ------------------------------------------------------


def setup(app):
    # Add custom Sphinx object type for Mopidy's config values
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )


# -- General configuration ----------------------------------------------------

needs_sphinx = "5.3"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.graphviz",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
]

project = "Mopidy"
copyright = "2009-2025, Stein Magnus Jodal and contributors"  # noqa: A001


release = version("Mopidy")
version = ".".join(release.split(".")[:2])

# To make the build reproducible, avoid using today's date in the manpages
today = "2025"

exclude_trees = ["_build"]

pygments_style = "sphinx"

modindex_common_prefix = ["mopidy."]


# -- Options for HTML output --------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_use_modindex = True
html_use_index = True
html_split_index = False
html_show_sourcelink = True

htmlhelp_basename = "Mopidy"

# Set canonical URL from the Read the Docs Domain
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")


# -- Options for LaTeX output -------------------------------------------------

latex_documents = [
    (
        "index",
        "Mopidy.tex",
        "Mopidy Documentation",
        "Stein Magnus Jodal and contributors",
        "manual",
    ),
]


# -- Options for manpages output ----------------------------------------------

man_pages = [
    ("command", "mopidy", "music server", "", "1"),
]


# -- Options for autodoc extension --------------------------------------------

autodoc_mock_imports = [
    "dbus",
    "mopidy.internal.gi",
]

typehints_document_rtype = True
typehints_use_signature = False
typehints_use_signature_return = True


# -- Options for extlink extension --------------------------------------------

extlinks = {
    "issue": ("https://github.com/mopidy/mopidy/issues/%s", "#%s"),
    "commit": ("https://github.com/mopidy/mopidy/commit/%s", "commit %s"),
    "js": ("https://github.com/mopidy/mopidy.js/issues/%s", "mopidy.js#%s"),
    "mpris": (
        "https://github.com/mopidy/mopidy-mpris/issues/%s",
        "mopidy-mpris#%s",
    ),
    "discuss": (
        "https://discourse.mopidy.com/t/%s",
        "discourse.mopidy.com/t/%s",
    ),
}


# -- Options for intersphinx extension ----------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pykka": ("https://pykka.readthedocs.io/stable/", None),
    "tornado": ("https://www.tornadoweb.org/en/stable/", None),
}

# -- Options for linkcheck builder -------------------------------------------

linkcheck_ignore = [  # Some sites work in browser but linkcheck fails.
    r"http://localhost:\d+/",
    r"http://wiki.commonjs.org",
    r"http://vk.com",
    r"http://$",
]

linkcheck_anchors = False  # This breaks on links that use # for other stuff
