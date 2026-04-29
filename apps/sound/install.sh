#!/bin/bash
#
# Install the sound control web server.
#

# Install any dependencies if not installed.
DEBIAN_DEPS="python3"
for pkg in $DEBIAN_DEPS ; do
    dpkg -s $pkg > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
        apt-get install $pkg
    fi
done

# Install any python dependencies.
PYTHON_DEPS="flask jsmin daemonize simpleaudio rtmidi-python"
for pkg in $PYTHON_DEPS ; do
    pip3 show $pkg | grep Location: > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
        pip3 install $pkg
    fi
done

# Install our patched version of simpleaudio.
pushd simpleaudio-1.0.1
python3 setup.py build
python3 setup.py install
popd

# Create the necessary directories.
/usr/bin/install -m 0755 -d /usr/local/bin
/usr/bin/install -m 0755 -d /usr/local/lib/harmoniscope/sound
/usr/bin/install -m 0755 -d /etc/harmoniscope
/usr/bin/install -m 0755 -d /usr/local/share/harmoniscope/sounds
/usr/bin/install -m 0777 -d /var/log/harmoniscope

# Copy the program over.
/usr/bin/install -m 0755 bin/sound_server.py /usr/local/bin/

# Copy the libraries over.
/usr/bin/install -m 0644 lib/sound/*.py /usr/local/lib/harmoniscope/sound/

# Copy the sound files over.
/usr/bin/install -m 0644 sounds/*.wav /usr/local/share/harmoniscope/sounds/

# Remove the old init.d script that starts the daemon on boot.
rm -f /etc/init.d/sound-server 
rm -f /etc/rc?.d/???sound-server 

# Install the systemd config that starts the sound server.
/usr/bin/install -m 0755 etc/systemd/sound-server.service /etc/systemd/system

# Install the configuration for the software mixers.
/usr/bin/install -m 0644 ../../asound.conf /etc/asound.conf

# Configure the sound-server process to run at startup.
/bin/systemctl daemon-reload
/bin/systemctl enable sound-server.service
