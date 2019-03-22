#
# Project makefile for a LMC Base Classes project. You should normally only need to modify
# DOCKER_REGISTRY_USER and PROJECT below.
#

#
# DOCKER_REGISTRY_HOST, DOCKER_REGISTRY_USER and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for DOCKER_REGISTRY_HOST (=rnexus.engageska-portugal.pt) and overwrites
# DOCKER_REGISTRY_USER and PROJECT to give a final Docker tag of
# nexus.engageska-portugal.pt/dishmaster/dishmaster
#
DOCKER_REGISTRY_USER:=tango-example
PROJECT = lmcbaseclasses

#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
#
include .make/Makefile.mk

#
# IMAGE_TO_TEST defines the tag of the Docker image to test
#
IMAGE_TO_TEST = $(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(PROJECT):latest

#
# CACHE_VOLUME is the name of the Docker volume used to cache eggs and wheels
# used during the test procedure. The volume is not used during the build
# procedure
#
# TODO: WORKS LOCALLY
# CACHE_VOLUME = lmcbaseclasses-test-cache
# TODO: WORKS CI/CD
CACHE_VOLUME = $(PROJECT)-test-cache

# optional docker run-time arguments
DOCKER_RUN_ARGS =

#
# Defines a default make target so that help is printed if make is called
# without a target
#
.DEFAULT_GOAL := help

# TODO: WORKS LOCALLY
# DOCKER_NETWORK := $(shell echo "$(notdir $(CURDIR))"_default | tr -d "-" | tr A-Z a-z)
# TODO: WORKS CI/CD
DOCKER_NETWORK := $(shell echo "$(notdir $(CURDIR))"_default | tr A-Z a-z)

#
# defines a function to copy the ./test-harness directory into the container
# and then runs the requested make target in the container. The container is:
#
#   1. attached to the network of the docker-compose test system
#   2. uses a persistent volume to cache Python eggs and wheels so that fewer
#      downloads are required
#   3. uses a transient volume as a working directory, in which untarred files
#      and test output can be written in the container and subsequently copied
#      to the host
#
make = tar -c test-harness/ | \
	   docker run -i --rm --network=$(DOCKER_NETWORK) \
	   -e TANGO_HOST=databaseds:10000 \
	   -v $(CACHE_VOLUME):/home/tango/.cache \
	   --volumes-from=rsyslog-lmcbaseclasses:rw \
	   -v /build -w /build -u tango $(DOCKER_RUN_ARGS) $(IMAGE_TO_TEST) \
	   bash -c "sudo chown -R tango:tango /build && \
	   tar x --strip-components 1 --warning=all && \
	   sudo ln -sf /var/run/rsyslog/dev/log /dev/log && \
	   make TANGO_HOST=databaseds:10000 $1"

test: DOCKER_RUN_ARGS = --volumes-from=$(BUILD)
test: build  ## test the application
	$(INIT_CACHE)
	DOCKER_REGISTRY_HOST=$(DOCKER_REGISTRY_HOST) DOCKER_REGISTRY_USER=$(DOCKER_REGISTRY_USER) docker-compose up -d
	$(call make,test); \
	  status=$$?; \
	  rm -fr build; \
	  docker cp $(BUILD):/build .; \
	  docker rm -f -v $(BUILD); \
	  docker logs $(CACHE_VOLUME); \
	  docker logs $(CACHE_VOLUME) > build/container.log 2>&1; \
	  DOCKER_REGISTRY_HOST=$(DOCKER_REGISTRY_HOST) DOCKER_REGISTRY_USER=$(DOCKER_REGISTRY_USER) docker-compose down; \
	  exit $$status

pull:  ## download the application image
	docker pull $(IMAGE_TO_TEST)

up: build  ## start develop/test environment
	DOCKER_REGISTRY_HOST=$(DOCKER_REGISTRY_HOST) DOCKER_REGISTRY_USER=$(DOCKER_REGISTRY_USER) docker-compose up -d

piplock: build  ## overwrite Pipfile.lock with the image version
	docker run $(IMAGE_TO_TEST) cat /app/Pipfile.lock > $(CURDIR)/Pipfile.lock

interactive: up
interactive:  ## start an interactive session using the project image (caution: R/W mounts source directory to /app)
	docker run --rm -it --name=$(PROJECT)-dev -e TANGO_HOST=databaseds:10000 --network=$(DOCKER_NETWORK) \
          -v $(CURDIR):/app --volumes-from=rsyslog-lmcbaseclasses:rw $(IMAGE_TO_TEST) /bin/bash

down:  ## stop develop/test environment and any interactive session
	docker ps | grep $(PROJECT)-dev && docker stop $(PROJECT)-dev || true
	DOCKER_REGISTRY_HOST=$(DOCKER_REGISTRY_HOST) DOCKER_REGISTRY_USER=$(DOCKER_REGISTRY_USER) docker-compose down

help:  ## show this help.
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: all test up down help

# Creates Docker volume for use as a cache, if it doesn't exist already
INIT_CACHE = \
	docker volume ls | grep $(CACHE_VOLUME) || \
	docker create --name $(CACHE_VOLUME) -v $(CACHE_VOLUME):/cache $(IMAGE_TO_TEST)

# http://cakoose.com/wiki/gnu_make_thunks
BUILD_GEN = $(shell docker create -v /build $(IMAGE_TO_TEST))
BUILD = $(eval BUILD := $(BUILD_GEN))$(BUILD)