FROM artefact.skao.int/ska-tango-images-pytango-builder:9.5.0 AS buildenv
RUN apt-get update && apt-get install -y gnupg2 graphviz plantuml nano
RUN poetry self update -n 1.8.2
ENV LC_ALL en_US.UTF-8