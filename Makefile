#
# Project makefile for a SKA Tango Base project. You should normally only need to modify
# DOCKER_REGISTRY_USER and PROJECT below.

# Use bash shell with pipefail option enabled so that the return status of a
# piped command is the value of the last (rightmost) command to exit with a
# non-zero status. This lets us pipe output into tee but still exit on test
# failures.
SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -c

# DOCKER_REGISTRY_HOST, DOCKER_REGISTRY_USER and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for DOCKER_REGISTRY_HOST (=rnexus.engageska-portugal.pt) and overwrites
# DOCKER_REGISTRY_USER and PROJECT to give a final Docker tag of
# nexus.engageska-portugal.pt/ska-telescope/ska_tango_base
#
DOCKER_REGISTRY_USER:=ska-telescope
PROJECT = ska_tango_base
IMAGE_FOR_DIAGRAMS = nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:9.3.3.1
#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make lint', 'make test', etc.) are defined in this file.
#
include .make/Makefile.mk

.DEFAULT_GOAL := help

test: ## test ska_tango_base Python code
	mkdir -p build/reports
	python3 setup.py test | tee build/setup_py_test.stdout

lint: ## lint ska_tango_base Python code
	python3 -m pip install -U pylint==2.4.4
	python3 -m pip install pylint2junit
	mkdir -p build/reports
	pylint --output-format=parseable src/ska_tango_base | tee build/code_analysis.stdout
	pylint --output-format=pylint2junit.JunitReporter src/ska_tango_base > build/reports/linting.xml

test-in-docker: build ## Build the docker image and run tests inside it.
	@docker run --rm $(IMAGE):$(VERSION) make test

lint-in-docker: build ## Build the docker image and run lint inside it.
	@docker run --rm $(IMAGE):$(VERSION) make lint

generate-diagrams-in-docker: ## Build the docker image and generate state machine diagrams inside it.
	@docker run --rm -v $(PWD):/diagrams $(IMAGE_FOR_DIAGRAMS) bash -c "cd /diagrams && make generate-diagrams-in-docker-internals"

generate-diagrams-in-docker-internals:  ## Generate state machine diagrams (within a container!)
	test -f /.dockerenv  # ensure running in docker container
	apt-get update
	apt-get install --yes graphviz graphviz-dev gsfonts pkg-config
	python3 -m pip install pygraphviz
	cd /diagrams/docs/source && python3 draw_state_machines.py
	ls -lo /diagrams/docs/source/images/

help:  ## show this help.
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test lint test-in-docker lint-in-docker help
