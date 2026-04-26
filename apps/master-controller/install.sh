#!/bin/bash
#
# Install the master control daemon.
#

# Create the necessary directories.
/usr/bin/install -m 0755 -d /usr/local/bin
/usr/bin/install -m 0755 -d /usr/local/lib/harmoniscope/master
/usr/bin/install -m 0755 -d /usr/local/lib/harmoniscope/master/events
/usr/bin/install -m 0755 -d /etc/harmoniscope
/usr/bin/install -m 0755 -d /etc/harmoniscope/event_scripts
/usr/bin/install -m 0777 -d /var/log/harmoniscope
/usr/bin/install -m 0777 -d /var/run/harmoniscope

# Copy the program over.
/usr/bin/install -m 0755 bin/master_ctl.py /usr/local/bin/

# Copy the libraries over.
/usr/bin/install -m 0644 lib/master/*.py /usr/local/lib/harmoniscope/master/
/usr/bin/install -m 0644 lib/master/events/*.py /usr/local/lib/harmoniscope/master/events

# Remove the old init.d script that starts the daemon on boot.
rm -f /etc/init.d/master-controller 
rm -f /etc/rc?.d/???master-controller 

# Install the systemd config that starts the master controller.
/usr/bin/install -m 0755 etc/systemd/master-controller.service /etc/systemd/system

# Copy the controller configuration.
/usr/bin/install -m 0644 etc/harmoniscope/controller_config.json /etc/harmoniscope/

# Copy the event scripts.
/usr/bin/install -m 0644 etc/harmoniscope/event_scripts/*.json /etc/harmoniscope/event_scripts

# Configure the master-controller process to run at startup.
/bin/systemctl daemon-reload
/bin/systemctl enable master-controller.service

