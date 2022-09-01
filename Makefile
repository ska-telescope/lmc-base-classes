#
# Project makefile for a SKA Tango Base project. 
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.

PROJECT = ska-tango-base
IMAGE_FOR_DIAGRAMS = artefact.skao.int/ska-tango-images-pytango-builder:9.3.28

#PYTHON_RUNNER = poetry run

PYTHON_SWITCHES_FOR_ISORT = --skip-glob=*/__init__.py
PYTHON_SWITCHES_FOR_BLACK = --line-length 88
PYTHON_TEST_FILE = tests
PYTHON_VARS_AFTER_PYTEST = --forked

## Paths containing python to be formatted and linted
PYTHON_LINT_TARGET = src/ tests/

DOCS_SOURCEDIR=./docs/src
DOCS_SPHINXOPTS=-W --keep-going -n

#
# include makefile to pick up the standard Make targets, e.g., 'make build'

include .make/oci.mk
include .make/k8s.mk
include .make/python.mk
include .make/raw.mk
include .make/base.mk
include .make/docs.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

# Add this for typehints & static type checking
# Remove the -e (exclude) when formatting complete
python-post-format:
	$(PYTHON_RUNNER) docformatter -r -i --wrap-summaries 88 --wrap-descriptions 72 --pre-summary-newline $(PYTHON_LINT_TARGET)

python-post-lint:
	$(PYTHON_RUNNER) mypy --config-file mypy.ini $(PYTHON_LINT_TARGET)

#python-post-test: ## test ska_tango_base Python code
#	scripts/validate-metadata.sh

python-pre-test:
	python3 -m pip install --extra-index-url https://artefact.skao.int/repository/pypi-all/simple debugpy ska-ser-logging ska-tango-testing

docs-pre-build:
	python3 -m pip install -r docs/requirements.txt

.PHONY: python-post-format python-post-lint python-pre-test docs-pre-build
