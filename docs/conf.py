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
release = '1.2.12'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'myst_parser',  # Support for Markdown files
    'sphinxemoji.sphinxemoji',  # Emoji support in HTML and PDF
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

# Alabaster theme options for better path wrapping
html_theme_options = {
    'code_font_size': '0.8em',
    'page_width': '1200px',
}

# PDF output with XeLaTeX for Unicode emoji support
latex_engine = 'xelatex'

latex_elements = {
    'preamble': r'''
\usepackage{fontspec}
\setmainfont{DejaVu Sans}
\setmonofont[Scale=0.85]{DejaVu Sans Mono}
\usepackage{seqsplit}
\usepackage{xurl}
\usepackage{breakurl}
\usepackage{ragged2e}
\usepackage{microtype}
\sloppy
\emergencystretch=3em
\tolerance=9999
\hbadness=9999
% Wrap long paths and code with smaller font
\renewcommand{\path}[1]{{\small\seqsplit{#1}}}
\renewcommand{\sphinxcode}[1]{{\small\seqsplit{#1}}}
\renewcommand{\sphinxupquote}[1]{{\small\seqsplit{#1}}}
% Force verbatim to use smaller font and break long lines
\makeatletter
\renewcommand{\sphinxVerbatim}[1][1]{%
  \par\setbox\sphinxcodeblockbox=\hbox{%
    \fvset{fontsize=\small,baselinestretch=1}%
    \begin{OriginalVerbatim}[#1,commandchars=\\\{\}]%
}
% Allow breaking in table of contents
\renewcommand{\@pnumwidth}{2em}
\renewcommand{\@tocrmarg}{3em}
\makeatother
''',
    'fontpkg': r'\usepackage{fontspec}',
    'printindex': r'\footnotesize\raggedright\printindex',
    'tableofcontents': r'\sphinxtableofcontents',
    'maxlistdepth': '10',
    'fncychap': '',
}

# LaTeX document settings
latex_use_parts = False
latex_show_pagerefs = True
latex_show_urls = 'footnote'

latex_documents = [
    ('index', 'pyarchinit-mini.tex', 'pyarchinit-mini Documentation',
     'pyarchinit-mini Team', 'manual', True),
]
