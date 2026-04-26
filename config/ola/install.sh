#!/bin/bash
#
# Install the fluidsynth configuration and startup files. Run as root.

if [ "$UID" -ne 0 -a "$EUID" -ne 0 ] ; then
    echo "Run this script as root."
    exit 
fi

# Copy files.
/usr/bin/install -D -b ola-port.conf /etc/ola/
/usr/bin/install -D -b ola-universe.conf /etc/ola/

