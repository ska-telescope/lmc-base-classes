#
# Project makefile for a SKA Tango Base project. 

PROJECT = ska-tango-base
IMAGE_FOR_DIAGRAMS = artefact.skao.int/ska-tango-images-pytango-builder:9.3.28

# E203 and W503 conflict with black, line line set to 110 for long intersphinx doc strings
# A003 shadowing python builtin
PYTHON_SWITCHES_FOR_FLAKE8 = --extend-ignore=BLK,T --enable=DAR104 --ignore=A003,E203,FS003,W503,N802 --max-complexity=10 \
    --docstring-style=SPHINX  --max-line-length=110 --rst-roles=py:attr,py:class,py:const,py:exc,py:func,py:meth,py:mod \
    --rst-directives=uml

PYTHON_SWITCHES_FOR_ISORT = --skip-glob=*/__init__.py
PYTHON_SWITCHES_FOR_BLACK = --line-length 88
PYTHON_TEST_FILE = tests
## Paths containing python to be formatted and linted
## Replace with src & tests when all completed
PYTHON_LINT_TARGET = src/ska_tango_base/base \
    src/ska_tango_base/obs/obs_state_model.py \
    src/ska_tango_base/subarray/subarray_obs_state_model.py \
    src/ska_tango_base/commands.py \
    src/ska_tango_base/executor.py \
    src/ska_tango_base/testing/mock/mock_callable.py

DOCS_SPHINXOPTS=-n -W --keep-going

#
# include makefile to pick up the standard Make targets, e.g., 'make build'

include .make/oci.mk
include .make/k8s.mk
include .make/helm.mk
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
	$(PYTHON_RUNNER) mypy --config-file mypy.ini --exclude src/ska_tango_base/csp/ $(PYTHON_LINT_TARGET)

#python-do-test:
#	mkdir -p build/reports
#	python3 setup.py test | tee build/setup_py_test.stdout
 
python-post-test: ## test ska_tango_base Python code
	scripts/validate-metadata.sh
	 
python-pre-test:
	python3 -m pip install --extra-index-url https://artefact.skao.int/repository/pypi-all/simple debugpy ska-ser-logging ska-tango-testing

docs-pre-build:
	python3 -m pip install -r docs/requirements.txt

.PHONY: python-post-format python-post-lint


<<<<<<< HEAD
generate-diagrams-in-docker: ## Generate state machine diagrams using a container.
	@docker run --rm -v $(PWD):/project $(IMAGE_FOR_DIAGRAMS) bash -c "cd /project && make generate-diagrams-in-docker-internals"

generate-diagrams-in-docker-internals:  ## Generate state machine diagrams (within a container!)
	test -f /.dockerenv  # ensure running in docker container
	apt-get update
	apt-get install --yes graphviz graphviz-dev gsfonts pkg-config
	python3 -m pip install pygraphviz
	cd /project && python3 -m pip install .
	cd /project/docs/src && python3 scripts/draw_state_machines.py
	ls -lo /project/docs/src/api/*/*.png

docs-in-docker: ## Generate docs inside a container
	@docker build -t ska_tango_base_docs_builder  . -f docs/Dockerfile
	@docker run --rm -v $(PWD):/project --user $(id -u):$(id -g) ska_tango_base_docs_builder

help:  ## show this help.
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test test-in-docker lint-in-docker help
=======
>>>>>>> 347fafc (MCCS-934 typehint and static type check)
