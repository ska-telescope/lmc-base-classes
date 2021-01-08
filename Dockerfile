# Use SKA python image as base image
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:9.3.3.1 AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:9.3.3.1 AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

# Note: working dir is `/app` which will have a copy of our repo
# The pip install will be a "user installation" so update path to access console scripts
ENV PATH=/home/tango/.local/bin:$PATH
RUN python3 -m pip install -e . --user
CMD ["SKABaseDevice"]
