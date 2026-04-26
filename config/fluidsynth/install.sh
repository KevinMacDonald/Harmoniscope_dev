#!/bin/bash
#
# Install the fluidsynth configuration and startup files. Run as root.

if [ "$UID" -ne 0 -a "$EUID" -ne 0 ] ; then
    echo "Run this script as root."
    exit 
fi

# Copy files.
/usr/bin/install -D -b config.txt /etc/fluidsynth/
/usr/bin/install -D -b fluidsynth.init.sh /etc/init.d/fluidsynth.sh

# Update the init script numbers.
/usr/sbin/update-rc.d fluidsynth.sh defaults
