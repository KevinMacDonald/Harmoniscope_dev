# constants.py - General use constants.

from master.system_state import SystemState

# The maximum voltage value for an analog knob input.
MAX_KNOB_VOLTAGE = 5.0

# The number of knobs at each station.
KNOB_COUNT = 4

# The number of knob positions.
KNOB_POSITION_COUNT = 8

# The default log file to use.
DEFAULT_LOG_FILE = "/var/log/harmoniscope/master-controller.log"

# The file to use to record our process ID (for background operation)
DAEMON_PID_FILE = "/var/run/master-controller.pid"

# The default file to use for the station configuration.
DEFAULT_STATION_CONFIG_FILE = "/etc/harmoniscope/controller_config.json"

# The default light server host.
DEFAULT_LIGHT_SERVER = "light"

# The default MIDI instrument to use.
DEFAULT_MIDI_INSTRUMENT = 15

# The default MIDI note velocity.
DEFAULT_NOTE_VELOCITY = 127

# How long to display the visual hint for, in seconds.
VISUAL_HINT_TIME = 0.5

# How long to wait for an update before we consider a station as dead and
# ignore it when we try to figure out whether to trigger the main event.
STATION_TIMEOUT = 300 # seconds

# The maximum number of pixels we have.
MAX_PIXELS = 512

# Default directory to look for event scripts in.
DEFAULT_EVENT_SCRIPT_DIR = "/etc/harmoniscope/event_scripts/"

# Event script filenames
IDLE_EVENT_SCRIPT = "idle_events.json"
MAIN_EVENT_SCRIPT = "main_event.json"

# Mappings of states to event scripts
EVENT_SCRIPT_MAPPING = {
    SystemState.STATE_RUNNING:     IDLE_EVENT_SCRIPT,
    SystemState.STATE_MAIN_EVENT:  MAIN_EVENT_SCRIPT
}
