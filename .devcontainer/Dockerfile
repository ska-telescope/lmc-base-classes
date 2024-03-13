FROM artefact.skao.int/ska-tango-images-pytango-builder:9.5.0 AS buildenv
RUN apt-get update && apt-get install -y gnupg2 graphviz plantuml nano

# Install newer version of poetry as a binary
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.8.1
RUN mkdir -p $POETRY_HOME && curl -sSL https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/main/install-poetry.py --output $POETRY_HOME/install-poetry.py
RUN cd $POETRY_HOME && POETRY_VERSION=${POETRY_VERSION} python3 install-poetry.py --yes
RUN /opt/poetry/bin/poetry --help
RUN ln -sfn /opt/poetry/bin/poetry /usr/local/bin/poetry