#!/usr/bin/env python3
#
# Sound server implementation
#
# Run:
#
#    ./sound-server.py
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
# well
if not __file__.startswith("/usr/local/bin"):
    sys.path.append(os.path.dirname(__file__) + "/../lib/")

# Pull the rest of the libraries from the installed location
sys.path.append("/usr/local/lib/harmoniscope")

from flask import Flask, request

from sound.constants        import *
from sound.web_service      import WebService
from sound.sound_player     import SoundPlayer

# Options dictionary
options = None

# Print out a usage statement and exit
def usage():
    print("Usage: ", __file__, " [options]")
    print("")
    print("  -h, --help               Print this help")
    print("  -f, --foreground         Run in the foreground (not as a daemon)")
    print("  -d, --sound-directory    The directory containing sound files")
    print("  -l, --log-file=FILE      Specify the file to log activity to")
    print("  -v, --verbose            Set the log level to verbose")
    sys.exit(-1)

# Parse the command-line options
def parse_options(argv):
    options = {
        "background":       True,
        "log-file":         DEFAULT_LOG_FILE,
        "sound-directory":  DEFAULT_SOUND_DIRECTORY
    }

    try:
        opts, args = getopt.getopt(argv,
                                    "hfd:l:v",
                                    [
                                        "help",
                                        "foreground",
                                        "log-file=",
                                        "sound-directory=",
                                        "verbose"
                                    ])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-v", "--verbose"):
            options["verbose"] = True
        if opt in ("-f", "--foreground"):
            options["background"] = False
        if opt in ("-l", "--log-file"):
            options["log-file"] = arg
        if opt in ("-d", "--sound-directory"):
            options["sound-directory"] = arg

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

    logging.debug("Starting the sound server")

    player     = SoundPlayer(options)
    web_server = WebService(options, player)

    web_server.start()

##
## End main code
##

if __name__ == '__main__':
    # Parse the command-line options.
    options = parse_options(sys.argv[1:])

    if options['background']:
        daemon = Daemonize(app="sound_server", pid=DAEMON_PID_FILE, action=main)
        daemon.start()

    else:
        main()
