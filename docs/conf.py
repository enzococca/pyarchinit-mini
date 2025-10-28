# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PyArchInit-Mini'
copyright = '2025, PyArchInit Team'
author = 'PyArchInit Team'
release = '1.6.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'myst_parser',  # Support for Markdown files
]

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/images/pyarchinit-mini-logo.png'

# Theme options
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'style_nav_header_background': '#2E86AB',
}

# PDF output with pdflatex (more compatible)
latex_engine = 'pdflatex'

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': r'''
\usepackage{hyperref}
\setcounter{secnumdepth}{0}
''',
}

# LaTeX document settings
latex_use_parts = False
latex_show_pagerefs = True
latex_show_urls = 'footnote'

# Single PDF output
latex_documents = [
    ('index', 'pyarchinit-mini.tex', 'PyArchInit-Mini Documentation',
     'PyArchInit Team', 'manual'),
]

# Ensure single PDF output
latex_additional_files = []
