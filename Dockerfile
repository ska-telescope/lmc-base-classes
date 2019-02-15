# Use SKA python image as base image
FROM ska-registry.av.it.pt/ska-docker/ska-python-buildenv:latest AS buildenv
FROM ska-registry.av.it.pt/ska-docker/ska-python-runtime:latest AS runtime

# create ipython profile to so that itango doesn't fail if ipython hasn't run yet
RUN ipython profile create

# set working directory
WORKDIR /app

#install lmc-base-classes
USER root
RUN buildDeps="ca-certificates git" \
   && DEBIAN_FRONTEND=noninteractive apt-get update \
   && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends $buildDeps \
   && su tango -c "git clone https://github.com/ska-telescope/lmc-base-classes.git" \
   && apt-get purge -y --auto-remove $buildDeps \
   && rm -rf /var/lib/apt/lists/* /home/tango/.cache

USER tango

CMD ["/venv/bin/python", "/app/skabase/SKABaseDevice/SKABaseDevice.py"]