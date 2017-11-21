FROM ubuntu:14.04

# Update the repo info
RUN apt-get update

# Install and configure supervisor
RUN apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

# Change installation dialogs policy to noninteractive, otherwise
# debconf raises errors: unable to initialize frontend: Dialog
ENV DEBIAN_FRONTEND noninteractive

# Avoid ERROR: invoke-rc.d: policy-rc.d denied execution of start.
RUN sed -i "s/^exit 101$/exit 0/" /usr/sbin/policy-rc.d

# Install apt utilities and common properties
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y software-properties-common \
                       python-software-properties
RUN apt-get update

# Install deb packages
RUN apt-get install -y --force-yes aptitude \
                       libffi-dev \
                       build-essential \
                       git-core \
                       python-dev \
                       python-pip \
                       libboost-python-dev \
                       screen \
                       xauth \
                       lsof

# Upgrade pip to latest
RUN pip install --upgrade pip


# Installing ansible
RUN add-apt-repository -y ppa:ansible/ansible
RUN apt-get update
RUN apt-get install -y ansible

# Install common software properties
RUN apt-get install -y software-properties-common
RUN apt-get update

# Add tango ppa for latest tango core
RUN add-apt-repository ppa:lmc-cam-ska/tango
RUN apt-get update

# Install mysql
RUN apt-get install -y mysql-client-5.6 \
                       mysql-client-core-5.6 \
                       mysql-server-5.6 \
                       mysql-server-core-5.6

# Install tango core packages
RUN apt-get install -y tango-db \
                       tango-common \
                       tango-starter \
                       tango-test \
                       tango-accesscontrol \
                       liblog4tango5v5 \
                       libtango9 \
                       libtango-doc \
                       libtango-dev \
                       liblog4tango-dev \
                       liblog4tango-doc


# Pip install tango support packages
#RUN pip install numpy \
#                ipython \
#                fandango \
##                tango-simlib \
#                jsonschema \
#                pytest \
#                mock

# Pip install itango cli
#RUN pip install tango-admin \
#                six \
#                itango

# Install virtual monitor
RUN apt-get install -y xvfb

# Configure virtual monitor env variable
ENV DISPLAY=:1.0

# Make home directory
RUN mkdir /home/tango
ENV HOME /home/tango

# Create a bashrc file
RUN touch /home/tango/.bashrc

# Expose connection
ENV ORB_PORT=10000
ENV TANGO_HOST=127.0.0.1:${ORB_PORT}
EXPOSE ${ORB_PORT}

# Create user
RUN useradd -ms /bin/bash tango
USER tango

# Configure supervisord
COPY supervisord.conf /etc/supervisor/conf.d/

# Start supervisor as deamon
CMD ["/usr/bin/supervisord"]
