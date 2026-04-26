#!/usr/bin/env python3
#
# Web server to control the lights via DMX.
#
# Run:
#
#    ./light_server.py
#
# See the README.txt file for more information.

import logging
import sys
import os.path
import getopt

from daemonize        import Daemonize
from logging.handlers import RotatingFileHandler

# If we're running out of the git repository, pull libraries from there as
# well.
if not __file__.startswith("/usr/local/bin/"):
    sys.path.append(os.path.dirname(__file__) + "/../lib/")

# Pull the rest of the libraries from the installed location.
sys.path.append("/usr/local/lib/harmoniscope")

from flask import Flask, request

from light.constants       import *
from light.web_service     import WebService
from light.light_simulator import LightSimulator
from light.workitem        import WorkItem
from light.worker          import Worker

# Options dictionary
options = None

# Print out a usage statement and exit
def usage():
    print("Usage: ", __file__, " [options]")
    print("")
    print("  -h, --help               Print this help")
    print("  -f, --foreground         Run in the foreground (not as a daemon)")
    print("  -c, --pixel-config=FILE  Use this pixel simulator config file")
    print("  -s, --enable-simulator   Enable the pixel simulator (default OFF)")
    print("  -d, --disable-dmx        Don't write DMX out (default ENABLED)")
    print("  -l, --log-file=FILE      Specify the file to log activity to")
    print("  -v, --verbose            Set the log level to verbose")
    sys.exit(-1)

# Parse the command-line options
def parse_options(argv):
    options = {
        "background":       True,
        "pixel-config":     PIXEL_CONFIG_FILE,
        "enable-simulator": False,
        "disable-dmx":      False,
        "log-file":         DEFAULT_LOG_FILE
    }

    try:
        opts, args = getopt.getopt(argv,
                                    "fhc:sdl:v",
                                    [
                                        "help",
                                        "foreground",
                                        "pixel-config=",
                                        "enable-simulator",
                                        "disable-dmx",
                                        "log-file=",
                                        "verbose"
                                    ])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-f", "--foreground"):
            options["background"] = False
        if opt in ("-c", "--pixel-config"):
            options["pixel-config"] = arg
        if opt in ("-s", "--enable-simulator"):
            options["enable-simulator"] = True

            # With the simulator, we can't run as a daemon.
            options["background"] = False

        if opt in ("-d", "--disable-dmx"):
            options["disable-dmx"] = True
        if opt in ("-v", "--verbose"):
            options["verbose"] = True
        if opt in ("-l", "--log-file"):
            options["log-file"] = arg

    return options

# Configure logging.
def initialize_logging(options):
    logger = logging.getLogger()

    if 'verbose' in options:
        level = logging.DEBUG
    else:
        level = logging.INFO


    # Create console handler and set level to debug.
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create a file handler and set level to warn. Limit each log file to 10MB
    # and keep five versions of the log file.
    fh = RotatingFileHandler(options['log-file'], 
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
    initialize_logging(options)

    # Create the UI application.
    if options["enable-simulator"] == True:
        simulator = LightSimulator(options["pixel-config"])

    # Create the DMX interface.
    try:
        from light.dmx             import DMXControl
        dmx = DMXControl(MAX_PIXEL)
    except ImportError:
        options["disable-dmx"] = True

    callbacks = []
    if options["enable-simulator"] == True:
        callbacks.append(simulator)
    if options["disable-dmx"] == False:
        callbacks.append(dmx)

    logging.info("Light server launched.")

    # Worker thread
    worker = Worker(callbacks)
    worker.start()

    # Start the web server application.
    web_service = WebService(worker)
    web_service.start()

    # If the simulator's enabled, just run that. Otherwise, wait for the
    # web service thread to end.
    if options["enable-simulator"] == True:
        simulator.run()
    else:
        web_service.join()

    logging.info("Main code done.")

##
## End main code
##

if __name__ == '__main__':
    # Parse the command-line options.
    options = parse_options(sys.argv[1:])

    if options['background']:
        daemon = Daemonize(app="light_server", pid=DAEMON_PID_FILE, action=main)
        daemon.start()

    else:
        main()


