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

# The ABElectronics IOPi library doesn't have a setup.py, so it can't be
# installed with pip. Instead, we manually copy the required library files
# to the same directory as the daemon executable.
/usr/bin/install -m 0644 ../../lib/ABElectronics_Python_Libraries/IOPi/ABE_IoPi.py /usr/local/bin/
/usr/bin/install -m 0644 ../../lib/ABElectronics_Python_Libraries/IOPi/ABE_helpers.py /usr/local/bin/

# The legacy ABElectronics Python library uses a mix of tabs and spaces for indentation, 
# which causes a fatal TabError in Python 3. Convert all tabs to 4 spaces to fix this.
sed -i 's/\t/    /g' /usr/local/bin/ABE_IoPi.py /usr/local/bin/ABE_helpers.py

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
