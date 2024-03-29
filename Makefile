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
IMAGE_FOR_DIAGRAMS = nexus.engageska-portugal.pt/ska-tango-images/pytango-builder:9.3.3.3


# import some standard Make targets e.g. `make build` (for building
# docker images), ``make push` (docker push procedure), etc.
include .make/Makefile.mk

# import make targets for code linting e.g. `make lint`
include .make/lint.mk

.DEFAULT_GOAL := help

test: ## test ska_tango_base Python code
	mkdir -p build/reports
	python3 setup.py test | tee build/setup_py_test.stdout

test-in-docker: build ## Build the docker image and run tests inside it.
	@docker run --rm $(IMAGE):$(VERSION) make test

lint-in-docker: build ## Build the docker image and run lint inside it.
	@docker run --rm $(IMAGE):$(VERSION) make lint

generate-diagrams-in-docker: ## Generate state machine diagrams using a container.
	@docker run --rm -v $(PWD):/project $(IMAGE_FOR_DIAGRAMS) bash -c "cd /project && make generate-diagrams-in-docker-internals"

generate-diagrams-in-docker-internals:  ## Generate state machine diagrams (within a container!)
	test -f /.dockerenv  # ensure running in docker container
	apt-get update
	apt-get install --yes graphviz graphviz-dev gsfonts pkg-config
	python3 -m pip install pygraphviz
	cd /project && python3 -m pip install .
	cd /project/docs/source && python3 scripts/draw_state_machines.py
	ls -lo /project/docs/source/api/*/*.png

docs-in-docker: ## Generate docs inside a container
	@docker build -t ska_tango_base_docs_builder  . -f docs/Dockerfile
	@docker run --rm -v $(PWD):/project --user $(id -u):$(id -g) ska_tango_base_docs_builder

help:  ## show this help.
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test test-in-docker lint-in-docker help
