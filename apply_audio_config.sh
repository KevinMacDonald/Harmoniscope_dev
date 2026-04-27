#!/bin/bash
#
# This script copies the asound.conf file to the correct system location
# to set the USB sound card as the default audio device.
#

# Test to see if we're root.
if [[ $UID != 0 ]] ; then
    echo "You must run this as root"
    exit -1
fi

echo "Copying asound.conf to /etc/asound.conf..."
cp asound.conf /etc/asound.conf

echo ""
echo "Configuration applied. A reboot is required for this change to take effect."
echo "You can reboot now by running: sudo reboot"