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

# Install base deb packages
RUN apt-get install -y --force-yes \
                        language-pack-en \
                        bind9-host \
                        tmux \
                        screen \
                        mosh \
                        psmisc \
                        python \
                        python-pip \
                        python-dev \
                        rsync \
                        vim \
                        wget \
                        build-essential \
                        apt-transport-https \
                        software-properties-common \
                        perl \
                        perl-modules \
                        git

# Remove some packages from the base template
RUN apt-get -y purge postfix

# Upgrade pip to latest
RUN pip install --upgrade pip

# Installing ansible
RUN add-apt-repository -y ppa:ansible/ansible
RUN apt-get update
RUN apt-get install -y ansible

# Install other deb packages
RUN apt-get install -y --force-yes \
                        aptitude \
                        libffi-dev \
                        build-essential \
                        git-core \
                        language-pack-en-base \
                        libatk1.0-dev \
                        libcairo2-dev \
                        libevent-dev \
                        libfontconfig1-dev \
                        libfreetype6-dev \
                        libpng12-dev \
                        libpq-dev \
                        python-cairo-dev \
                        libboost-python-dev \
                        gfortran \
                        screen \
                        zlib1g-dev \
                        tzdata \
                        ntpdate \
                        liblapack-dev \
                        libf2c2-dev \
                        libatlas-base-dev \
                        libssl0.9.8 \
                        man-db \
                        manpages \
                        ftp \
                        gawk \
                        telnet \
                        unzip \
                        tcpdump \
                        xauth \
                        lsof

# Install mysql
RUN apt-get install -y mysql-client-core-5.6 \
                       mysql-client-5.6 \
                       mysql-server-5.6

# Add tango ppa for latest tango core
RUN add-apt-repository ppa:lmc-cam-ska/tango
RUN apt-get update

# Install tango core packages
RUN apt-get install -y tango-common \
                       liblog4tango5v5 \
                       libtango9 \
                       libtango-doc \
                       libtango-dev \
                       liblog4tango-dev \
                       liblog4tango-doc

# Start mysql & install tango database packages
RUN service mysql start && apt-get install -y \
                       tango-db \
                       tango-starter \
                       tango-test \
                       tango-accesscontrol

# Pip install tango support packages
RUN pip install numpy \
                enum34 \
                ipython \
                fandango \
                tango-simlib \
                jsonschema \
                pytest \
                mock

# Pip install itango cli
RUN pip install tango-admin \
                six \
                itango

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

# Configure supervisord
COPY supervisord.conf /etc/supervisor/conf.d/

# Start supervisor as deamon
CMD ["/usr/bin/supervisord"]
