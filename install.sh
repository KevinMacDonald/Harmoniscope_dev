#!/bin/bash
#
# Install everything.
#

# Test to see if we're root.
if [[ $UID != 0 ]] ; then
    echo "You must run this as root"
    exit -1
fi

# Install any debian dependencies.
DEBIAN_DEPS="python3 python3-pip"
for pkg in $DEBIAN_DEPS ; do
    dpkg -s $pkg > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
        apt-get install $pkg
    fi
done

# Install any python dependencies.
PYTHON_DEPS="flask jsmin"
for pkg in $PYTHON_DEPS ; do
    pip3 show $pkg | grep Location: > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
        pip3 install $pkg
    fi
done

APPS="config/station-setup apps/light apps/control-scan apps/master-controller apps/sound"

for app in $APPS ; do 
    pushd $app && ./install.sh
    popd
done

# Re-run the station configuration.
/usr/local/bin/station_setup.py -d -n
