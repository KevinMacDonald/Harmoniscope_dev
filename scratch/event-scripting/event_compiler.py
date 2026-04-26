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

from copy import deepcopy
from random import randint, random
from time import sleep, time
from queue import PriorityQueue

MAX_PIXELS            = 512
DEFAULT_INPUT_SCRIPT  = "sample_event_input.json"
DEFAULT_OUTPUT_SCRIPT = "sample_event_compiled.json"

# If we're running out of the git repository, pull libraries from there as
# well.
if not __file__.startswith("/usr/local/bin/"):
    sys.path.append(os.path.dirname(__file__) + "/../lib/")

# Pull the rest of the libraries from the installed location.
sys.path.append("/usr/local/lib/harmoniscope")

# Wrapper function for a color value.
class Color:
    # Initialize the color.
    def __init__(self, value = { "red": 0, "blue": 0, "green": 0, "white": 0 }):
        self.set(value)

    # Set the color value.
    def set(self, value):
        if isinstance(value, Color):
            self.red   = value.red
            self.green = value.green
            self.blue  = value.blue
            self.white = value.white
            return

        self.red   = value["red"]
        self.green = value["green"]
        self.blue  = value["blue"]

        # White values are optional.
        if "white" in value:
            self.white = value["white"]
        else:
            self.white = 0

    # Add the value to this color.
    def add(self, value):
        self.red   += value.red
        self.green += value.green
        self.blue  += value.blue
        self.white += value.white
  
# Print out a usage statement and exit
def usage():
    print("Usage: ", __file__, " [options]")
    print("")
    print("  -h, --help               Print this help")
    print("  -i, --input-script=FILE  Use this event script input file")
    print("  -o, --output-script=FILE Write this output script file")
    sys.exit(-1)

# Parse the command-line options
def parse_options(argv):
    options = {
        "input-script":     DEFAULT_INPUT_SCRIPT,
        "output-script":    DEFAULT_OUTPUT_SCRIPT
    }

    try:
        opts, args = getopt.getopt(argv,
                                    "hi:o:",
                                    [
                                        "help",
                                        "input-script=",
                                        "output-script="
                                    ])

    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-i", "--input-script"):
            options["input-script"] = arg
        if opt in ("-o", "--output-script"):
            options["output-script"] = arg

    return options

# Load in the pixel configuration file, and return a queue of events, sorted by
# start time.
def load_event_script(input_script):
    with open(input_script) as config_file:
        # Use JSMin to remove the comments in the config file.
        minified = jsmin.jsmin(config_file.read())

        # Parse the JSON into a Python object.
        events = json.loads(minified)

        queue = PriorityQueue()
        for event in events["events"]:
            event["next-time"] = event["start-time"]
            queue.put([get_priority(event), event])

        return queue

# Get the event's priority.
def get_priority(event):
    return event["next-time"] * 10000000000 + int(random() * 10000000)

# Generate a delay event.
def create_delay_event(amount):
    return { "type": "delay", "amount": round(amount * 1000, 4) }

# Generate a pixel-set event.
def create_pixel_set_event(pixel, color):
    return { 
        "type":     "pixel-set", 
        "pixel":    pixel,
        "red":      int(color.red),
        "green":    int(color.green),
        "blue":     int(color.blue),
        "white":    int(color.white),
    }

# Generate the next step in a pixel fade event.
def process_pixel_fade(clock, pixels, event):
    steps = event["steps"]
    if "initialized" not in event:
        steps       = event["steps"]
        start_color = event["start-color"]
        end_color   = event["end-color"]

        event["step-time"] = (event["end-time"] - event["start-time"]) / steps

        color_step  = Color({
            "red":      (end_color["red"]   - start_color["red"])/steps,
            "green":    (end_color["green"] - start_color["green"])/steps,
            "blue":     (end_color["blue"]  - start_color["blue"])/steps,
            })

        # White values are optional.
        if "white" in end_color and "white" in start_color:
            color_step.white = (end_color["white"] - start_color["white"])/steps

        event["color-step"]  = color_step

        event["cur-color"]   = Color(event["start-color"])
        event["initialized"] = True

    else:
        cur_color = event["cur-color"]
        event["cur-color"].add(event["color-step"])
    
    event["next-time"] = event["next-time"] + event["step-time"]
    if event["next-time"] >= event["end-time"]:
        event["cur-color"] = Color(event["end-color"])
        event.pop("next-time")

    output_events = []
    for pixel in event["pixels"]:
        output_events.append(create_pixel_set_event(pixel, event["cur-color"]))

        if pixel != 0:
            pixels[pixel] = event["cur-color"]
        else:
            for i in range(0, MAX_PIXELS):
                pixels[i] = event["cur-color"]

    return (pixels, output_events)

# Generate the next step in a pixel chase event.
def process_pixel_chase(clock, pixels, event):
    if "initialized" not in event:
        steps = len(event["pixels"])
        event["step-time"]   = (event["end-time"] - event["start-time"]) / steps
        event["pixel-index"] = 0
        event["initialized"] = True

    output_events = []

    # Reset the current pixel back to it's stored color.
    cur_pixel = event["pixel-index"]
    if cur_pixel != 0:
        pixel_number = event["pixels"][cur_pixel - 1]
        pixels[pixel_number] = event["cur-color"]
        output_events.append(create_pixel_set_event(pixel_number, 
                                                    event["cur-color"]))

    # If we're past the last pixel, don't continue the crawl.
    if cur_pixel >= len(event["pixels"]):
        event.pop("next-time")
        return (pixels, output_events)

    # Stash the pixel's current color.
    pixel_number = event["pixels"][cur_pixel]
    event["cur-color"] = pixels[pixel_number]

    # Set it to the chase color.
    pixels[pixel_number] = event["color"] 
    output_events.append(create_pixel_set_event(pixel_number, 
                                                Color(event["color"])))

    # Advance to the next pixel.
    cur_pixel += 1 
    event["pixel-index"] = cur_pixel

    # Advance time.
    event["next-time"] = event["next-time"] + event["step-time"]

    return (pixels, output_events)

# Generate the next step in a pixel sparkle event.
def process_pixel_sparkle(clock, pixels, event):
    if "initialized" not in event:
        event["pixel-index"] = 0   # Keeps the index of the currently lit pixel.
        event["initialized"] = True

    output_events = []

    # Reset the current pixel back to it's stored color.
    cur_pixel = event["pixel-index"]
    if cur_pixel != 0:
        pixel_number = event["pixels"][cur_pixel - 1]
        pixels[pixel_number] = event["cur-color"]
        output_events.append(create_pixel_set_event(pixel_number, 
                                                    pixels[pixel_number]))

    # If we're past the end time, return.
    if clock >= event["end-time"]:
        event.pop("next-time")
        return (pixels, output_events)

    # Figure out what the next pixel we want to flash is.
    cur_pixel = randint(1, len(event["pixels"]))
    event["pixel-index"] = cur_pixel
    pixel_number = event["pixels"][cur_pixel - 1]

    # Stash the pixel's current color.
    event["cur-color"] = pixels[pixel_number]

    # Copy the current color, and set it to white.
    cur_color = pixels[pixel_number]
    pixels[pixel_number] = Color(cur_color)
    pixels[pixel_number].white = 255

    output_events.append(create_pixel_set_event(pixel_number, 
                                                pixels[pixel_number]))

    # Advance time.
    event["next-time"] = event["next-time"] + (random() * event["flash-rate"])

    return (pixels, output_events)

# Generate a pixel set event.
def process_pixel_set(clock, pixels, event):
    output_events = []

    for pixel in event["pixels"]:
        pixel_color = Color(event["start-color"])
        output_events.append(create_pixel_set_event(pixel, pixel_color))
        pixels[pixel] = pixel_color

    event.pop("next-time")
    return (pixels, output_events)

EVENT_TYPE_HANDLERS = {
    "pixel-fade":       process_pixel_fade,
    "pixel-set":        process_pixel_set,
    "pixel-chase":      process_pixel_chase,
    "pixel-sparkle":    process_pixel_sparkle
}

##
## Main routine
##

def main(argv):
    # Parse the command-line options.
    options = parse_options(argv)

    # Read in the event script.
    input_queue = load_event_script(options["input-script"])

    output_events = []
    clock         = 0
    pixels        = list()
    for i in range(0, MAX_PIXELS):
        pixels.append(Color())

    # Now run the events.
    while not input_queue.empty():
        (priority, event) = input_queue.get()

        # Update the clock, as appropriate.
        if (clock < event["next-time"]) and (round(event["next-time"] - clock, 4) != 0):
            output_events.append(create_delay_event(event["next-time"] - clock))
        clock = event["next-time"]

        # If we don't have a handler for this kind of event, ignore it.
        if event["type"] not in EVENT_TYPE_HANDLERS:
            print("Unknown event type:", event["type"])
            continue
        
        # Write a debugging statement.
        if "desc" not in event:
            event["desc"] = "(unknown)" 
        print(round(clock, 4), "Processing a", event["type"], "event:", event["desc"])

        # Call the handler to generate the appropriate low-level events.
        (pixels, new_events) = EVENT_TYPE_HANDLERS[event["type"]](clock, pixels, event)

        # If this high-level event has more events, put it back on the queue.
        if "next-time" in event:
            input_queue.put([get_priority(event), event])

        # Add the new events to the output queue.
        output_events.extend(new_events)

    # Optimization pass: only paint on the last pixel change of a sequence.
    # We do this by working backwards from the end of the list of output
    # events, setting a flag when we see a pixel-set event, and clearing it
    # when we see a delay (which indicates we should repaint).
    sequence = False
    for event in reversed(output_events):
        if event["type"] == "pixel-set":
            if sequence == False:
                event["paint"] = 1
                sequence = True
            else:
                event["paint"] = 0
    
        # Reset the sequence flag when we get to a delay event.
        if event["type"] == "delay":
            sequence = False
    
    # Write out the generated events.
    with open(options["output-script"], "w") as output_file:
        json.dump({"events": output_events}, output_file, indent=4)

##
## End main code
##

if __name__ == '__main__':
    main(sys.argv[1:])
