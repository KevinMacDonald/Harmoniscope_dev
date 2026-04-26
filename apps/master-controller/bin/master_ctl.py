#!/usr/bin/env python3
#
# Web server to coordinate all of the state and events in the Harmoniscope.
#
# Run:
#
#    ./master_controller.py
#
# See the README.txt file for more information.

import getopt
import logging
import os.path
import sys
import time

from daemonize        import Daemonize
from logging.handlers import RotatingFileHandler

# If we're running out of the git repository, pull libraries from there as
# well.
if not __file__.startswith("/usr/local/bin/"):
    sys.path.append(os.path.dirname(__file__) + "/../lib/")

# Pull the rest of the libraries from the installed location.
sys.path.append("/usr/local/lib/harmoniscope")

from master.constants       import *
from master.config          import Config
from master.web_service     import WebService
from master.update_queue    import UpdateWorker
from master.event_queue     import EventWorker
from master.state_tracker   import StateTracker

from master.events          import change_state

# Options dictionary
options = None

# Print out a usage statement and exit
def usage():
    print("Usage: ", __file__, " [options]")
    print("")
    print("  -h, --help                Print this help")
    print("  -c, --station-config=FILE Use this station configuration file")
    print("  -e, --event-scripts=DIR   Load event scripts from this directory")
    print("  -f, --foreground          Run in the foreground (not as a daemon)")
    print("  -i, --light-server=HOST   Send light updates to this host")
    print("  -l, --log-file=FILE       Specify the file to log activity to")
    print("  -s, --sound-server=HOST   Send all sound commands to this host")
    print("  -v, --verbose             Set the log level to verbose")
    print("")
    print("Hints:")
    print("  --[enable|disable]-visual-hint")
    print("  --[enable|disable]-audio-hint")
    sys.exit(-1)

# Parse the command-line options
def parse_options(argv):
    options = {
        "background":       True,
        "event-scripts":    DEFAULT_EVENT_SCRIPT_DIR,
        "light-server":     DEFAULT_LIGHT_SERVER,
        "log-file":         DEFAULT_LOG_FILE,
        "station-config":   DEFAULT_STATION_CONFIG_FILE,
        "visual-hint":      True,
        "audio-hint":       True
    }

    try:
        opts, args = getopt.getopt(argv,
                                    "hfi:l:e:c:s:v",
                                    [
                                        "help",
                                        "foreground",
                                        "light-server=",
                                        "event-scripts=",
                                        "station-config=",
                                        "log-file=",
                                        "sound-server=",
                                        "verbose",
                                        "enable-visual-hint",
                                        "disable-visual-hint",
                                        "enable-audio-hint",
                                        "disable-audio-hint"
                                    ])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-c", "--station-config"):
            options["station-config"] = arg
        if opt in ("-e", "--event-scripts"):
            options["event-scripts"] = arg
        if opt in ("-f", "--foreground"):
            options["background"] = False
        if opt in ("-i", "--light-server"):
            options["light-server"] = arg
        if opt in ("-l", "--log-file"):
            options["log-file"] = arg
        if opt in ("-s", "--sound-server"):
            options["sound-server"] = arg
        if opt in ("-v", "--verbose"):
            options["verbose"] = True
        if opt == "--enable-visual-hint":
            options["visual-hint"] = True
        if opt == "--disable-visual-hint":
            print("Disabling visual hint")
            options["visual-hint"] = False
        if opt == "--enable-audio-hint":
            options["audio-hint"] = True
        if opt == "--disable-audio-hint":
            options["audio-hint"] = False

    return options

# Configure logging.
def initialize_logging():
    logger = logging.getLogger()

    if Config.get('verbose'):
        level = logging.DEBUG
    else:
        level = logging.INFO


    # Create console handler and set level to debug.
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create a file handler and set level to warn. Limit each log file to 10MB
    # and keep five versions of the log file.
    fh = RotatingFileHandler(Config.get('log-file'), 
                             mode='a', 
                             maxBytes=10000000, 
                             backupCount=5)
    fh.setLevel(level)

    logging.basicConfig(level    = level,
                        format   = '%(asctime)s %(levelname)-8s %(message)s',
                        datefmt  = '%a, %d %b %Y %H:%M:%S',
                        handlers = [fh, ch])

    # Disable the info logs from the HTTP requests module.
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


##
## Main routine
##

def main():
    config = Config(options)

    initialize_logging()

    logging.debug("Visual hint: %s" % str(options["visual-hint"]))
    logging.debug("Audio hint: %s" % str(options["audio-hint"]))

    # Initialize the station state tracker.
    StateTracker.initialize()

    # Create the event dispatch thread.
    event_queue = EventWorker()
    event_queue.start()

    event = change_state.Event(when = time.time(),
                               new_state = SystemState.STATE_RUNNING)
    EventWorker.queue_event(event)

    # Create the station update processing thread.
    update_queue = UpdateWorker()
    update_queue.start()

    # Start the web server application.
    web_service = WebService(update_queue)
    web_service.run()

    logging.info("Main code done.")

##
## End main code
##

if __name__ == '__main__':
    # Parse the command-line options.
    options = parse_options(sys.argv[1:])

    if options['background']:
        daemon = Daemonize(app="master_ctl", pid=DAEMON_PID_FILE, action=main)
        daemon.start()

    else:
        main()

