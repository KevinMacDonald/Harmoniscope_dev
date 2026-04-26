#!/bin/bash
#
# Install the station setup scripts.
#

# Create the necessary directories.
/usr/bin/install -m 0755 -d /etc/harmoniscope

# Copy the configuration script over.
/usr/bin/install -m 0755 bin/station_setup.py /usr/local/bin/

# Copy the config files over.
/usr/bin/install -m 0644 etc/hosts /etc/
/usr/bin/install -m 0644 etc/network/interfaces /etc/network/
/usr/bin/install -m 0644 etc/harmoniscope/eth0.template /etc/harmoniscope/
/usr/bin/install -m 0644 etc/harmoniscope/station-mappings.json /etc/harmoniscope/
/usr/bin/install -m 0755 etc/init.d/station-setup /etc/init.d/

# Configure the station-setup process to run at startup.
/usr/sbin/update-rc.d station-setup defaults
