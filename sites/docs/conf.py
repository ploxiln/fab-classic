# Obtain shared config values
import os, sys
from os.path import abspath, join, dirname
sys.path.append(abspath(join(dirname(__file__), '..')))
sys.path.append(abspath(join(dirname(__file__), '..', '..')))
from shared_conf import *

extensions.extend(['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'releases'])

# Autodoc settings
autodoc_default_flags = ['members', 'special-members']

# Intersphinx connection to stdlib
intersphinx_mapping = {
    'python': ('https://docs.python.org/2.7', None),
}

# just used for old changelog
releases_github_path = "fabric/fabric"
releases_document_name = ["old_changelog"]
