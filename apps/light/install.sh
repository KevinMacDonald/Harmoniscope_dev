#!/bin/bash
#
# Install the light control web server.
#

# Install any python dependencies.
PYTHON_DEPS="flask jsmin daemonize"
for pkg in $PYTHON_DEPS ; do
    pip3 show $pkg | grep Location: > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
        pip3 install $pkg
    fi
done

# Create the necessary directories.
/usr/bin/install -m 0755 -d /usr/local/bin
/usr/bin/install -m 0755 -d /usr/local/lib/harmoniscope/light
/usr/bin/install -m 0755 -d /etc/harmoniscope
/usr/bin/install -m 0777 -d /var/log/harmoniscope

# Copy the program over.
/usr/bin/install -m 0755 bin/light_server.py /usr/local/bin/

# Copy the libraries over.
/usr/bin/install -m 0644 lib/light/*.py /usr/local/lib/harmoniscope/light/

# Remove the old init.d script that starts the daemon on boot.
rm -f /etc/init.d/light-server 
rm -f /etc/rc?.d/???light-server 

# Install the systemd config that starts the light server.
/usr/bin/install -m 0755 etc/systemd/light-server.service /etc/systemd/system

# Copy the simulator pixel configuration.
/usr/bin/install -m 0644 etc/harmoniscope/pixel_config.json /etc/harmoniscope/

# Configure the light-server process to run at startup.
/bin/systemctl daemon-reload
/bin/systemctl enable light-server.service

