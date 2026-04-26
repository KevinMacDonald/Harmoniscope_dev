#!/bin/bash
#
# Install the station control scanning daemon.
#

# Install any python dependencies.
PYTHON_DEPS="daemonize"
for pkg in $PYTHON_DEPS ; do
    pip3 show $pkg | grep Location: > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
        pip3 install $pkg
    fi
done

# Create the necessary directories.
/usr/bin/install -m 0755 -d /usr/local/bin
/usr/bin/install -m 0777 -d /var/log/harmoniscope/

# Copy the program over.
/usr/bin/install -m 0755 bin/control_scan.py /usr/local/bin/

# Remove the old init.d script that starts the daemon on boot.
rm -f /etc/init.d/control-scan 
rm -f /etc/rc?.d/???control-scan 

# Install the systemd config that starts the light server.
/usr/bin/install -m 0755 etc/systemd/control-scan.service /etc/systemd/system

# Configure the control-scan process to run at startup.
/bin/systemctl daemon-reload
/bin/systemctl enable control-scan.service
