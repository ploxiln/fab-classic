import alabaster

import sys
from os.path import abspath, join, dirname
sys.path.append(abspath(join(dirname(__file__), '..', '..')))

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
    'alabaster',
    'releases',
]

# Alabaster theme + mini-extension
html_theme_path = [alabaster.get_path()]
html_static_path = ['_shared_static']
html_theme = 'alabaster'
html_theme_options = {
    'logo': 'logo.png',
    'logo_name': True,
    'logo_text_align': 'center',
    'description': "Pythonic remote execution",
    'github_user': 'ploxiln',
    'github_repo': 'fab-classic',
    'github_type': 'star',
    'travis_button': True,
    'link': '#3782BE',
    'link_hover': '#3782BE',
}
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'searchbox.html',
    ]
}

# Regular settings
project = 'fab-classic'
copyright = 'Fabric authors'
master_doc = 'index'
templates_path = ['_templates']
exclude_trees = ['_build']
source_suffix = '.rst'
default_role = 'obj'

# Autodoc settings
autodoc_default_flags = ['members', 'special-members']

# Intersphinx connection to stdlib
intersphinx_mapping = {
    'python': ('https://docs.python.org/2.7', None),
}

# just used for old changelog
releases_github_path = "fabric/fabric"
releases_document_name = ["old_changelog"]
