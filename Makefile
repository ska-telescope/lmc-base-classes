#
# Project makefile for a LMC Base Classes project. You should normally only need to modify
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
# nexus.engageska-portugal.pt/tango-example/dishmaster
#
DOCKER_REGISTRY_USER:=tango-example
PROJECT = lmcbaseclasses

#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make lint', 'make test', etc.) are defined in this file.
#
include .make/Makefile.mk

.DEFAULT_GOAL := help

test: ## test lmcbaseclasses Python code
	mkdir -p build
	python3 setup.py test | tee build/setup_py_test.stdout
	mv coverage.xml build

lint: ## lint lmcbaseclasses Python code
	python3 -m pip install -U pylint==2.4.4
	python3 -m pip install pylint2junit
	mkdir -p build/reports
	pylint --output-format=parseable src/ska | tee build/code_analysis.stdout
	pylint --output-format=pylint2junit.JunitReporter src/ska > build/reports/linting.xml

test-in-docker: build ## Build the docker image and run tests inside it.
	@docker run $(IMAGE):$(VERSION) make test

lint-in-docker: build ## Build the docker image and run lint inside it.
	@docker run $(IMAGE):$(VERSION) make lint

help:  ## show this help.
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test lint test-in-docker lint-in-docker help
