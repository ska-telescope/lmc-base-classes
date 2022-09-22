# Use SKA python image as base image
FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.28 AS buildenv
FROM artefact.skao.int/ska-tango-images-pytango-runtime:9.3.14 AS runtime

# Install Poetry
USER root 
RUN python3 -m pip install poetry==1.1.13
RUN poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies and the app
RUN poetry install --no-dev -vvv

USER tango

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
#RUN ipython profile create

# Cannot use pip install -e with poetry
#RUN python3 -m pip install -e . --user
#CMD ["SKABaseDevice"]
