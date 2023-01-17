# Use SKA python image as base image
FROM artefact.skao.int/ska-tango-images-pytango-builder:9.3.34 AS buildenv
FROM artefact.skao.int/ska-tango-images-pytango-runtime:9.3.21 AS runtime

USER root 

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies and the app
RUN poetry config virtualenvs.create false && poetry install --only main

USER tango
