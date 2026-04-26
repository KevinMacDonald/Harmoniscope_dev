# constants.py - General use constants.

import sys
import os.path

# Maximum number of individual light sources in the structure
MAX_PIXEL = 50

# Maximum value of a DMX channel value
MAX_BRIGHTNESS = 255

# The default file that contains the pixel simulation mappings.
PIXEL_CONFIG_FILE = os.path.dirname(__file__) + "/../../etc/harmoniscope/pixel_config.json"

# The default log file to use.
DEFAULT_LOG_FILE = "/var/log/harmoniscope/light-server.log"

# The file to use to record our process ID (for background operation)
DAEMON_PID_FILE = "/var/run/light-server.pid"

