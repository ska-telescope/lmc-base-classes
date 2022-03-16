# Use SKA python image as base image
FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.28 AS buildenv
FROM artefact.skao.int/ska-tango-images-pytango-runtime:9.3.16 AS runtime

# Install Poetry
USER root 
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python -
RUN chmod a+x /opt/poetry/bin/poetry
RUN /opt/poetry/bin/poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies and the app
RUN /opt/poetry/bin/poetry install --no-dev

USER tango

# create ipython profile too so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

RUN python3 -m pip install -e . --user
CMD ["SKABaseDevice"]
