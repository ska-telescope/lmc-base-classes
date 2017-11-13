FROM ubuntu:14.04

# Update the repo info
RUN apt-get update
# Install and configure supervisor
RUN apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
# change installation dialogs policy to noninteractive, otherwise
# debconf raises errors: unable to initialize frontend: Dialog
ENV DEBIAN_FRONTEND noninteractive
# Install apt utilities and common properties
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y software-properties-common
# Install tango dependencies
RUN add-apt-repository ppa:lmc-cam-ska/tango && apt-get update
RUN apt-get install -y mysql-server-5.6 \ 
                       mysql-client-5.6 \
                       mysql-client-core-5.6 \
                       mysql-server-core-5.6 \
                       mysql-common-5.6

RUN service mysql start

RUN apt-get install -y libboost-python-dev \
                       dbconfig-common \
                       libtango-dev \
                       liblog4tango5v5 \
                       tango-starter \
                       tango-test \
                       tango-common \
                       tango-db 

# Avoid ERROR: invoke-rc.d: policy-rc.d denied execution of start.
RUN sed -i "s/^exit 101$/exit 0/" /usr/sbin/policy-rc.d

# Install some utilities
RUN apt-get install -y git \
                       python-pip \
                       vim \
                       ipython 

RUN pip install numpy
RUN pip install tango-simlib

# instal virtual monitor
RUN apt-get install -y xvfb

# configure virtual monitor env variable
ENV DISPLAY=:1.0

# Configure supervisord
COPY supervisord.conf /etc/supervisor/conf.d/

# copy & untar mysql tango database and change owner to mysql user
ADD tangodb-tiny.tar /var/lib/mysql/
RUN chown -R mysql /var/lib/mysql/tango
#sudo usermod -d /var/lib/mysql/ mysql

# Define tango host env var
ENV TANGO_HOST=172.17.0.2:10000

# add USER ENV (necessary for spyderlib in taurus.qt.qtgui.editor)
ENV USER=kat

# start supervisor as deamon
CMD ["/usr/bin/supervisord"]
