# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# https://sphinx-copybutton.readthedocs.io/en/latest/index.html

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'gerstnerhungarian'
copyright = '2023, Viktor Martinović'
author = 'Viktor Martinović'
version = '2.0'
release = '2.0'
extensions = ['sphinx.ext.autodoc', 'sphinx_copybutton']
html_theme = 'sphinx_rtd_theme'

# uncomment row below if problems with installation
autodoc_mock_imports = [
    "attr",
    "cldfbench",
    "clldutils",
    "lexibank_gerstnerhungarian",
    "loanpy",
    "lingpy",
    "pycldf",
    "pylexibank",
    "pysem",
    "spacy",
    "tabulate",
]
