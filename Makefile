#
# Project makefile for a SKA Tango Base project. You should normally only need to modify
# PROJECT below.

# Use bash shell with pipefail option enabled so that the return status of a
# piped command is the value of the last (rightmost) command to exit with a
# non-zero status. This lets us pipe output into tee but still exit on test
# failures.
SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -c

# CAR_OCI_REGISTRY_HOST, and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for CAR_OCI_REGISTRY_HOST (=artefact.skao.int) and overwrites
# PROJECT to give a final Docker tag of artefact.skao.int/ska-tango-base
PROJECT = ska-tango-base
IMAGE_FOR_DIAGRAMS = artefact.skao.int/ska-tango-images-pytango-builder:9.3.10

#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
#

# include OCI Images support
include .make/oci.mk

# Include Python support
include .make/python.mk

# include core make support
include .make/base.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak


.DEFAULT_GOAL := help

python-post-test: ## test ska_tango_base Python code
	scripts/validate-metadata.sh
	

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
