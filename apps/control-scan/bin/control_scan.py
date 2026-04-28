#!/usr/bin/env python3
#
# Daemon which reads the analog values of the 4 station control knobs, and 
# sends state changes to the master controller process.
#
# Run as root:
#
#    sudo ./control_scan.py
#
# See the README.txt file for more information.

# Import standard libraries.
import ads1256
import getopt
import logging
import os
import requests
import sys
import time

from daemonize        import Daemonize
from logging.handlers import RotatingFileHandler

# Import ABElectronics libraries for I/O board
try:
    from ABE_IoPi import IoPi as IOPi
except ImportError:
    from ABE_IoPi import IOPi

try:
    from ABE_helpers import ABEHelpers
except ImportError:
    from ABEHelpers import ABEHelpers

# The default master controller server name.
MASTER_HOST = "127.0.0.1"

# The base REST URL to submit control reports to.
MASTER_REPORT_URL = "http://{host}:7000/station/{station_id}"

# The file we can read to get this station's ID.
STATION_ID_FILE = "/var/local/harmoniscope/station-id"

# How long to wait between input scans.
INPUT_SCAN_INTERVAL = 0.01


# Note, this is old code that isn't needed with the new Multiplexer board. Keeping for reference only. - Mike
# How big of a difference between control readings we need to report a 
# change in knob position.
# INPUT_CHANGE_THRESHOLD = 0.1 # volts

# The default log file to use.
DEFAULT_LOG_FILE = "/var/log/harmoniscope/control-scan.log"

# How long, at most, to wait between station updates.
MAX_UPDATE_INTERVAL = 60 # seconds

# The file to use to record our process ID (for background operation)
DAEMON_PID_FILE = "/var/run/control-scan.pid"

# Options dictionary
options = None

# Print out a usage statement and exit
def usage():
    print("Usage: ", __file__, " [options]")
    print("")
    print("  -h, --help               Print this help")
    print("  -f, --foreground         Run in the foreground (not as a daemon)")
    print("  -m, --master-host=HOST   Send station updates to this host")
    print("  -i, --station-id=ID      Manually specify a station ID")
    print("  -d, --scan-interval=SECS Set the interval between input scans")
    print("  -l, --log-file=FILE      Specify the file to log activity to")
    print("  -v, --verbose            Set the log level to verbose")
    sys.exit(-1)

# Parse the command-line options
def parse_options(argv):
    options = {
        "background":       True,
        "master-host":      MASTER_HOST,
        "scan-interval":    INPUT_SCAN_INTERVAL,
        "log-file":         DEFAULT_LOG_FILE
    }

    # Read in the station ID
    with open(STATION_ID_FILE, "r") as f:
        options["station-id"] = f.read()

    try:
        opts, args = getopt.getopt(argv,
                                    "hfm:i:d:l:v",
                                    [ 
                                        "help", 
                                        "foreground", 
                                        "master-host=",
                                        "station-id=", 
                                        "scan-interval=", 
                                        "log-file=", 
                                        "verbose", 
                                    ])

    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-f", "--foreground"):
            options["background"] = False
        if opt in ("-m", "--master-host"):
            options["master-host"] = arg
        if opt in ("-i", "--station-id"):
            options["station-id"] = arg
        if opt in ("-d", "--scan-interval"):
            options["scan-interval"] = arg
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

# The code commented out below is the original code that Jon wrote to interface with the Waveshare board, which
# we have decommissioned in favor of the Multiplexer board. Keeping the old code for reference only until the new
# Multiplexer code has been fully tested. - Mike

# # Initialize the ADC.
# def initialize_ads1256():
#     ads1256.initialize()
#
#     # We configure it with a gain of 1 (no gain), and to sample at
#     # 1000 samples per second (SPS).
#     ads1256.configure(ads1256.ADS1256_GAIN_1, ads1256.ADS1256_100SPS)
#
# # Read in the analog values of the input knobs and return them as an array.
# def read_input_knobs():
#     return ads1256.read_channels(0, 3, ads1256.ADS1256_INPUT_SINGLE_ENDED)
#
# # Compare the two sets of inputs, and return True if they are the different.
# def inputs_are_different(a, b):
#     for val_a, val_b in zip(a, b):
#         # Check to see if the difference in voltages is greater than the
#         # threshold.
#         if abs(val_a - val_b) > INPUT_CHANGE_THRESHOLD:
#             return True
#     return False

# Send the updated input values to the master controller.
def send_station_update(url, values):
    params = { 
        "analog_values": ",".join(map(str, values))
    }

    try:
        logging.info("Sending control update to master: %s", params)
        response = requests.get(url, params = params)

    except requests.exceptions.RequestException as error:
        logging.error("Error sending update to master control service: %s", error)
        return False

    return True


# Initialize the Multiplexer board.
def initialize_multiplexer():
    # Instantiate bus objects for interfacing with the board's two buses
    i2c_helper = ABEHelpers()
    i2c_bus = i2c_helper.get_smbus()
    bus1 = IOPi(i2c_bus, 0x20)  # knobs 1 and 2
    bus2 = IOPi(i2c_bus, 0x21)  # knobs 3 and 4


    pin = 1

    while pin <= 16:  # Iterate through all 16 slots and configure them to be read
        # Pins can be either input or output. Setting the pin with a value of 1 makes it INPUT
        bus1.set_pin_direction(pin, 1)

        # We need to set the pullup resistor for the pin so that it has voltage. This inverts
        # the on/off which we will deal with below.
        bus1.set_pin_pullup(pin, 1)

        # We make the return value make logical sense by inverting the pin so that 1 is on, 0 is off.
        bus1.invert_pin(pin, 1)

        # repeat all the above for bus 2
        bus2.set_pin_direction(pin, 1)
        bus2.set_pin_pullup(pin, 1)
        bus2.invert_pin(pin, 1)

        pin += 1

    return True

# Read in the analog values of the input knobs and return them as an array.
def read_input_knobs():
    # Instantiate bus objects for interfacing with the board's two buses
    i2c_helper = ABEHelpers()
    i2c_bus = i2c_helper.get_smbus()
    bus1 = IOPi(i2c_bus, 0x20)
    bus2 = IOPi(i2c_bus, 0x21)

    # Initialize our input array
    knobinputs = [0, 0, 0, 0]

    # Iterate through all 16 slots on both buses
    pin = 1
    while pin <= 16:

        # Read the value of the pin on bus 1. If it's "on", add the results to our input array.
        if bus1.read_pin(pin) == 1:
            # Apply result appropriately based on the knob range: Knob 1 is 1-8, Knob 2 is 9-16.
            if pin <= 8:
                knobinputs[0] = pin
            else:
                knobinputs[1] = pin - 8

        # Do the same for knobs 3 and 4 on the bus 2.
        if bus2.read_pin(pin) == 1:
            if pin <= 8:
                knobinputs[2] = pin
            else:
                knobinputs[3] = pin - 8
        pin += 1

    return knobinputs



##
## BEGIN MAIN CODE
##

def main():

    initialize_multiplexer()
    initialize_logging(options)

    # Generate the report URL.
    report_url = MASTER_REPORT_URL.format(host       = options["master-host"],
                                          station_id = options["station-id"])
    logging.info("Control scan deamon launched.")
    logging.info("Sending station reports to: %s", report_url)

    # Initialize our cache of previous input values.
    previous_inputs = [0, 0, 0, 0]

    last_update_sent = 0

    # Now we loop forever (and ever, and ever, and ever...).
    while True:
        # Read in the current values of all of the analog lines.    
        current_inputs = read_input_knobs()

        if current_inputs != previous_inputs:
            # Send the updated values to the master control service.
            if send_station_update(report_url, current_inputs):
                # If we successfully sent the message, stash the inputs so 
                # we can only send updates when the values change.
                previous_inputs = current_inputs
                last_update_sent = time.time()

        else:
            # If it's been longer than the maximum update interval, force
            # send an update.
            if (time.time() - last_update_sent) > MAX_UPDATE_INTERVAL:
                send_station_update(report_url, previous_inputs)
                last_update_sent = time.time()

        # Wait for a while.
        time.sleep(options["scan-interval"])


##
## END MAIN CODE
##

# Glue code to call the main() function.
if __name__ == '__main__':
    if not os.geteuid() == 0:
        sys.exit('This tool must be run as root.')

    # Parse the command-line options.
    options = parse_options(sys.argv[1:])

    if options['background']:
        daemon = Daemonize(app="control_scan", pid=DAEMON_PID_FILE, action=main)
        daemon.start()

    else:
        main()
