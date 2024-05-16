# -*- coding: utf-8 -*-
#
# SKA Tango Base documentation build configuration file, created by
# sphinx-quickstart on Fri Jan 11 10:03:42 2019.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
#
# pylint: disable=all

import os
import sys


# Strip the @tango.DebugIt decorator from any class methods,
# as it removes the function signature which causes Sphinx to ignore the them.
def setup(app):  # type: ignore
    app.setup_extension("sphinx.ext.autodoc")

    def strip_decorator(func):  # type: ignore
        return func

    import tango

    original_decorator = tango.DebugIt

    # Monkey patch the original decorator
    def patched_decorator(*args, **kwargs):  # type: ignore
        return strip_decorator(original_decorator(*args, **kwargs))  # type: ignore

    tango.DebugIt = patched_decorator


# This is an elaborate hack to insert write property into _all_
# mock decorators. It is needed for getting @command to build
# in mocked out tango.server.  Also add dummy classes for
# attribute and device_property so that they at least
# appear in the docs, even if there is not other useful info.
# see https://github.com/sphinx-doc/sphinx/issues/6709
# from sphinx.ext.autodoc.mock import _MockObject
#
#
# def get_kwarg_comma_separated_values(kwargs):
#     pairs = (f"{key}={value}" for key, value in kwargs.items())
#     return ", ".join(pairs)
#
#
# class TangoKwargMethodMock:
#     def __init__(self, name, **kwargs):
#         self.name = name
#         self.kwargs = kwargs
#
#     def __repr__(self):
#         return f"{self.name}({get_kwarg_comma_separated_values(self.kwargs)})"
#
#
# def call_mock(self, *args, **kw):
#     from types import FunctionType, MethodType
#
#     if args and type(args[0]) in [type, FunctionType, MethodType]:
#         # Appears to be a decorator, pass through unchanged
#         args[0].write = lambda x: x
#         return args[0]
#
#     if repr(self) in ['tango.server.attribute', 'tango.server.device_property']:
#         return TangoKwargMethodMock(repr(self), **kw)
#
#     return self
#
#
# _MockObject.__call__ = call_mock
# # hack end

autodoc_mock_imports = [
    "debugpy",
    "numpy",
    "ska_ser_logging",
    "ska_tango_testing",
    "tango",
]

autodoc_default_options = {
    "member-order": "bysource",
}


# Both the class’ and the __init__ method’s docstring are concatenated and inserted.
autoclass_content = "both"


# -- Path set up --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../../src"))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "7.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.viewcode",
    "sphinxcontrib.plantuml",
    "recommonmark",
]
autoclass_content = "class"
plantuml_syntax_error_image = True


# Add any paths that contain templates here, relative to this directory.
# templates_path = []

# The suffix of source filenames.
source_suffix = [".rst", ".md"]

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "SKA Tango Base"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#


def get_release_info():  # type: ignore
    release_filename = os.path.join("..", "..", "src", "ska_tango_base", "release.py")
    exec(open(release_filename).read())
    return locals()


release_info = get_release_info()
copyright = release_info["copyright"]

# The short X.Y version.
version = release_info["version"]
# The full version, including alpha/beta/rc tags.
release = release_info["version"]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
# language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["orphans/*"]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "ska_ser_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

html_context = {}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = []

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = "SKA_TangoBasedoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "SKA_TangoBase.tex",
        "SKA Tango Base Documentation",
        "manual",
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "ska_tango_base", "SKA Tango Base Documentation", 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "SKA_TangoBase",
        "SKA Tango Base Documentation",
        "SKA_TangoBase",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "ska-control-model": (
        "https://developer.skao.int/projects/ska-control-model/en/latest/",
        None,
    ),
    "tango": ("https://pytango.readthedocs.io/en/v9.4.2/", None),
}

nitpicky = True

nitpick_ignore = [
    # ska-control-model API docs don't document the root package
    ("py:mod", "ska_control_model"),
    # TODO: Can't figure this one out
    ("py:class", "ska_tango_base.base.base_component_manager.Wrapped"),
    # These ones look like sphinx bugs
    ("py:class", "method"),
    ("py:class", "tango.server.command"),
    ("py:class", "tango.Logger"),
    ("py:class", "socket.SocketKind"),
    # These can't be found after stripping the tango.DebugIt decorator
    ("py:class", "tango._tango.Logger"),
    ("py:class", "tango._tango.DevState"),
    ("py:class", "tango._tango.DbDevInfo"),
    ("py:class", "tango._tango.DeviceProxy"),
    # Version of sphinx in use here doesn't support type variables
    ("py:class", "ska_tango_base.poller.poller.PollRequestT"),
    ("py:class", "ska_tango_base.poller.poller.PollResponseT"),
    ("py:class", "ska_tango_base.alarm_handler_device.ComponentManagerT"),
    ("py:class", "ska_tango_base.base.base_device.ComponentManagerT"),
    ("py:class", "ska_tango_base.capability_device.ComponentManagerT"),
    ("py:class", "ska_tango_base.commands.CommandReturnT"),
    ("py:class", "ska_tango_base.controller_device.ComponentManagerT"),
    ("py:class", "ska_tango_base.logger_device.ComponentManagerT"),
    ("py:class", "ska_tango_base.obs.obs_device.ComponentManagerT"),
    ("py:class", "ska_tango_base.subarray.subarray_device.ComponentManagerT"),
    ("py:class", "ska_tango_base.tel_state_device.ComponentManagerT"),
    (
        "py:class",
        "ska_tango_base.testing.reference.reference_base_component_manager.ComponentT",
    ),
    ("py:class", "ska_tango_testing.mock.tango.MockTangoEventCallbackGroup"),
    ("py:class", "P"),
]
