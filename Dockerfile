# Use SKA python image as base image
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-buildenv:latest AS buildenv
FROM nexus.engageska-portugal.pt/ska-docker/ska-python-runtime:latest AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

# A temporary workaround until system team can investigate why 'pipenv install -e .' doesn't work
RUN pip install -e . --extra-index-url https://nexus.engageska-portugal.pt/repository/pypi/simple
CMD ["/venv/bin/python", "/app/skabase/SKABaseDevice/SKABaseDevice.py"]
