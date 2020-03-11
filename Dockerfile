# Use SKA python image as base image
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:latest AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:latest AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

# Note: working dir is `/app` which will have a copy of our repo
RUN python3 -m pip install -e . --extra-index-url https://nexus.engageska-portugal.pt/repository/pypi/simple
CMD ["python3", "/app/skabase/SKABaseDevice/SKABaseDevice.py"]
