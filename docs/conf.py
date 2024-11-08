#!/usr/bin/env python3

import datetime

import globus_sdk

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# pull signature docs from type hints, into body
# and keep the signatures concise
autodoc_typehints = "description"
# do not generate doc stubs for inherited parameters from a superclass,
# merely because they are type annotated
autodoc_typehints_description_target = "documented_params"


# sphinx extensions (minimally, we want autodoc and viewcode to build the site)
# plus, we have our own custom extension in the SDK to include
extensions = [
    # sphinx-included extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    # other packages
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_issues",
    # our custom one
    "globus_sdk._sphinxext",
]

project = "globus-sdk"
copyright = f"2016-{datetime.datetime.today().strftime('%Y')}, Globus"
author = "Globus Team"
# The short X.Y version.
version = globus_sdk.__version__
# The full version, including alpha/beta/rc tags.
release = version

issues_github_path = "globus/globus-sdk-python"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]


# HTML Theme Options
html_show_sourcelink = True
html_theme = "furo"
html_title = "globus-sdk v3"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#27518F",
    },
}
html_logo = "_static/logo.png"
html_static_path = ["_static"]
html_css_files = ["css/globus_sdk_tab_borders.css"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"
pygments_dark_style = "monokai"  # this is a furo-specific option

# Output file base name for HTML help builder.
htmlhelp_basename = "globus-sdk-doc"
