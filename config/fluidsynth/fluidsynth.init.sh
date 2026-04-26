#!/bin/sh
# 
# Boot-time init script to start up fluidsynth. Relies on the framework in 
# /lib/init/init-d-script.
#
# Gets installed as /etc/init.d/fluidsynth.sh


# kFreeBSD do not accept scripts as interpreters, using #!/bin/sh and sourcing.
if [ true != "$INIT_D_SCRIPT_SOURCED" ] ; then
    set "$0" "$@"; INIT_D_SCRIPT_SOURCED=true . /lib/init/init-d-script
fi

### BEGIN INIT INFO
# Provides:          fluidsynth
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: FluidSynth software synthesizer
# Description:       Starts the FluidSynth software synthesizer and connects 
#                    it up to Alsa.
### END INIT INFO

# Author: Jon McClintock <jammer@weak.org>

DESC="FluidSynth software synthesizer"
DAEMON="/usr/bin/fluidsynth"

# Arguments to pass to start-stop-daemon:
#
# -b: Background the process, because it doesn't do it automatically.
START_ARGS="-b"

# FluidSynth options:
#
# -s: Start as a server process.
# -i: Disable the interactive shell, we don't need it.
# -f: Load configuration from the specified file.
# -a: Use the ALSA audio driver.
# -m: Use the ALSA MIDI driver.
#
# The last argument is the SoundFont file to load.
DAEMON_ARGS="-si -f /etc/fluidsynth/config.txt -a alsa -m alsa_seq /usr/share/sounds/sf2/FluidR3_GM.sf2"
