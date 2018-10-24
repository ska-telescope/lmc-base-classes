# -*- coding: utf-8 -*-

# Imports
import sys
import os
# Path handling
conf_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(conf_dir, os.path.pardir))
sys.path.insert(0, os.path.join(conf_dir, os.path.pardir, os.path.pardir))

# Configuration
extensions = ['sphinx.ext.autodoc', 'devicedoc']
master_doc = 'index'

# Data
project = u'SKALogger'
copyright = u""""""
