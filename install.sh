#!/bin/bash
#
# Install everything.
#

# Test to see if we're root.
if [[ $UID != 0 ]] ; then
    echo "You must run this as root"
    exit -1
fi

# --- System Package Repository Fix ---
# Your Raspberry Pi is running Raspbian Jessie, which is an old, archived version.
# The following command will completely overwrite your sources list to point
# to the correct legacy package archive.
echo "Updating package sources for Raspbian Jessie..."
cat > /etc/apt/sources.list << EOF
deb http://legacy.raspbian.org/raspbian/ jessie main contrib non-free rpi
# Uncomment line below then 'apt-get update' to enable 'apt-get source'
# deb-src http://legacy.raspbian.org/raspbian/ jessie main contrib non-free rpi
EOF

# Update package lists and install essential system-level dependencies.
# We need curl to fix pip.
echo "Installing Debian packages..."
apt-get update && apt-get install -y python3 curl python3-smbus i2c-tools

# --- Python Pip Fix ---
# The version of pip available for Jessie is broken. We will manually install
# a working version of pip for Python 3.4 using the official bootstrap script.
# We first check if pip3 is functional to avoid reinstalling it on every run.
echo "Installing Python packages..."
if ! pip3 --version > /dev/null 2>&1; then
    echo "pip3 is not working or not found. Reinstalling..."
    curl https://bootstrap.pypa.io/pip/3.4/get-pip.py -o get-pip.py
    # We must constrain the pip version to one compatible with Python 3.4, as noted in the logs.
    python3 get-pip.py "pip<19.2" "setuptools<45" wheel
fi
pip3 install -r requirements.txt

# --- Application Installation ---
APPS="config/station-setup apps/light apps/control-scan apps/master-controller apps/sound"

for app in $APPS ; do 
    pushd $app && ./install.sh
    popd
done

# Re-run the station configuration to restart daemons with the new code.
echo "Restarting Harmoniscope services..."
/usr/local/bin/station_setup.py -d
