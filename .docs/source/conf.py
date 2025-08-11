# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "UV Template Project"
copyright = "2025, Template Author"
author = "Template Author"
release = "0.1.8"  # Updated to match pyproject.toml


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Source file suffixes ----------------------------------------------------
source_suffix = {
    ".rst": None,
    ".md": "myst_parser",
}

# -- MyST parser configuration -----------------------------------------------
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "dollarmath",
    "amsmath",
]
