#
# Project makefile for a SKA Tango Base project.
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
include .make/base.mk
include .make/raw.mk

PROJECT = ska-tango-base

#####################
# PYTHON
#####################
include .make/python.mk

IMAGE_FOR_DIAGRAMS = artefact.skao.int/ska-tango-images-pytango-builder:9.3.28
PYTHON_LINE_LENGTH = 88
PYTHON_VARS_AFTER_PYTEST = --forked

python-post-lint:
	$(PYTHON_RUNNER) mypy --config-file mypy.ini $(PYTHON_LINT_TARGET)

python-pre-test:
	python3 -m pip install --extra-index-url https://artefact.skao.int/repository/pypi-all/simple debugpy ska-ser-logging ska-tango-testing

.PHONY: python-post-lint python-pre-test


#####################
# DOCS
#####################
include .make/docs.mk

DOCS_SPHINXOPTS=-W --keep-going

docs-pre-build:
	poetry config virtualenvs.create false
	poetry install --no-root --only docs

.PHONY: docs-pre-build


# include your own private variables for custom deployment configuration
-include PrivateRules.mak



