# constants.py - General use constants.

import sys
import os.path

# The default log file to use.
DEFAULT_LOG_FILE = "/var/log/harmoniscope/sound-server.log"

# The file to use to record our process ID (for background operation)
DAEMON_PID_FILE = "/var/run/sound-server.pid"

# The default directory for sound files.
DEFAULT_SOUND_DIRECTORY = "/usr/local/share/harmoniscope/sounds/"

# MIDI note value range
MIDI_NOTE_MAX = 88
MIDI_NOTE_MIN = 1

# Instrument number range
INSTRUMENT_NUMBER_MAX = 15
INSTRUMENT_NUMBER_MIN = 0

# MIDI note velocity range
MIDI_VELOCITY_MIN = 0
MIDI_VELOCITY_MAX = 127
