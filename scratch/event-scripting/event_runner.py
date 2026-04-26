#!/usr/bin/env python3
#
# event_runner.py - Run an event script against the light and sound services.
#

import getopt
import json
import jsmin
import os.path
import requests
import sys

from time import sleep, time

DEFAULT_INPUT_SCRIPT = "sample_event.json"
DEFAULT_LIGHT_SERVER = "localhost"

# If we're running out of the git repository, pull libraries from there as
# well.
if not __file__.startswith("/usr/local/bin/"):
    sys.path.append(os.path.dirname(__file__) + "/../lib/")

# Pull the rest of the libraries from the installed location.
sys.path.append("/usr/local/lib/harmoniscope")

# Print out a usage statement and exit
def usage():
    print("Usage: ", __file__, " [options]")
    print("")
    print("  -h, --help               Print this help")
    print("  -i, --input-script=FILE  Use this event script file")
    print("  -l, --light-server=HOST  Which host is running the light server")
    sys.exit(-1)

# Parse the command-line options
def parse_options(argv):
    options = {
        "input-script":     DEFAULT_INPUT_SCRIPT,
        "light-server":     DEFAULT_LIGHT_SERVER
    }

    try:
        opts, args = getopt.getopt(argv,
                                    "hi:l:",
                                    [
                                        "help",
                                        "input-script=",
                                        "light-server="
                                    ])

    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-i", "--input-script"):
            options["input-script"] = arg
        if opt in ("-l", "--light-server"):
            options["light-server"] = arg

    return options

# Load in the pixel configuration file.
def load_event_script(input_script):
    with open(input_script) as config_file:
        # Use JSMin to remove the comments in the config file.
        minified = jsmin.jsmin(config_file.read())

        # Parse the JSON into a Python object.
        return json.loads(minified)

# Run a delay event.
def process_delay_event(state, event):
    state["schedule_time"] += int(event["amount"]) / 1000
    delay_time = state["schedule_time"] - time()
    if round(delay_time, 4) > 0:
        sleep(delay_time)
    print("Schedule time:", round(state["schedule_time"], 2), 
          "Actual:", round(time(), 2),
          "Delta:", round(state["schedule_time"] - time(), 2))

# Run a pixel set event.
def process_pixel_set_event(state, event):
    url = ("http://" + state["light-server"] + 
            ":8000/light/" + 
            str(event["pixel"]))

    params = { 
            'r': event["red"],
            'g': event["green"],
            'b': event["blue"],
            'w': event["white"],
            'p': event["paint"]
            }
    try:
        response = requests.get(url, params)
        response.raise_for_status()

    except requests.exceptions.RequestException as error:
        print("Error sending update to light service:", error)


##
## Main routine
##

def main(argv):
    # Parse the command-line options.
    options = parse_options(argv)

    # Set up our time tracking variable.
    options["schedule_time"] = time()

    # Read in the event script.
    script = load_event_script(options["input-script"])

    # Now run the events.
    for event in script["events"]:
        if event["type"] == "delay":
            process_delay_event(options, event)

        elif event["type"] == "pixel-set":
            process_pixel_set_event(options, event)

        else:
            print("Unknown event type:", event["type"])
        
    

##
## End main code
##

if __name__ == '__main__':
    main(sys.argv[1:])
