#!/usr/bin/env bash
echo -e "\n==== Configuring ELT TANGO ====\n"

export SETUPDIR=$ELT_PATH/eltbase/setup

# Adding repositories to aptitude
PPA_TANGO="http://ppa.launchpad.net/tango-controls/core/ubuntu"
if ! grep -q $PPA_TANGO /etc/apt/sources.list /etc/apt/sources.list.d/* ; then
  sudo add-apt-repository 'deb http://ppa.launchpad.net/tango-controls/core/ubuntu precise main'
  sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A8780D2D6B2E9D50
  sudo apt-key update
  sudo apt-get -qq update
fi

# Setting parameters for packages which generate input prompts
sudo apt-get install -y debconf-utils
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password password"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password password"
sudo debconf-set-selections <<< "tango-common tango-common/tango-host string `echo $HOSTNAME:10000`"
sudo debconf-set-selections <<< "tango-db tango-db/mysql/admin-pass password password"
sudo debconf-set-selections <<< "tango-db tango-db/password-confirm password password"
sudo debconf-set-selections <<< "tango-db tango-db/app-password-confirm password password"
sudo debconf-set-selections <<< "tango-db tango-db/mysql/app-pass password password"
sudo debconf-set-selections <<< "tango-db tango-db/dbconfig-install boolean true"

# Installing required system packages
echo "Installing required system packages"
sudo apt-get -q install --force-yes --yes $(grep -vE "^\s*#" requirements.apt  | tr "\n" " ")

# Installing tango
echo "Installing Tango"
sudo apt-get -q install --force-yes --yes tango-common tango-db tango-starter tango-test libtango8-dev libtango8-doc libtango-java

# Install required python packages
pushd python > /dev/null
pip install -r requirements.pip
popd > /dev/null

# Install PyTango
easy_install -U PyTango==8.1.8

# Setting up Ganglia configuration
# Copy configuration files to their destination
sudo cp setup/config/ganglia/gmetad.conf /etc/ganglia/gmetad.conf
sudo cp setup/config/ganglia/gmond.conf /etc/ganglia/gmond.conf

# Restart ganglia services
sudo service ganglia-monitor restart && sudo service gmetad restart

# Install Elettra Alarm database
echo "Setting up Elettra alarm database"
./setup/config/deploy/db.sh password

# Compile Elettra alarm and add it to device tree
if [ ! -f $ELT_PATH/eltbase/run/Alarm ]; then
    echo "Compiling Elettra alarm database"
    export ELETTRA_ALARM_SRC_DIR=$ELT_PATH/aavs-tango/3rdparty/alarm-server/src
    sudo rm -rf -d $ELETTRA_ALARM_SRC_DIR/*.o
    make -C $ELETTRA_ALARM_SRC_DIR
    cp $ELETTRA_ALARM_SRC_DIR/Alarm $ELT_PATH/aavs-tango/python/run/Alarm
else
    echo "Elettra alarm device exists, skipping compile"
fi

echo "Setting up Log directory"
sudo mkdir -p $ELT_LOG/tango
# Tango starter runs under user tango, so all device servers stared by it will be run as user tango
# so give ownership to the log directory to tango
sudo chown tango:tango $ELT_LOG/tango

echo "Setting up starter properties"

# Set the log directory and startup path properties in the TANGO starter device
sudo chmod +x ./setup/config/deploy/tango_starter_properties.py
./setup/config/deploy/tango_starter_properties.py $ELT_LOG $ELT_PATH

# Restart the TANGO starter for changes to take effect
sudo service tango-starter restart
echo "Wait for tango-starter restart"
sleep 5
echo "Setting up elt_ctl utility"

# Set up elt_sctl utility in $ELT_BIN
# elt_ctl utility used to configure, run, and get the status of device servers
./setup/config/deploy/elt_ctl.sh

echo "Setting up upstart job"
# Create upstart job to call "elt_ctl --run" on startup.
./setup/config/deploy/aavs-init-setup.sh

# Link default configuration file
if [ ! -f $ELT_CONFIG/tango_servers_config.py ]; then
  ln -s $PWD/eltbase/config/servers_config.py $ELT_CONFIG/tango_servers_config.py
fi
