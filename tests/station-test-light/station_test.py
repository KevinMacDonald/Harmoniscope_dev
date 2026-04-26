#!/usr/bin/python3
#
# Simple program to demonstrate reading inputs from the hardware and controlling
# the color of an RGB can light connected over USB.
#
# Run as root:
#
#    ./station_test.py
#
# See the README.txt file for more information.

# Import standard libraries.
import time

# Import our custom libraries from the 'hw' subdirectory.
from hw.analog_inputs  import AnalogInputs
from hw.color_selector import ColorSelector
from hw.dmx_control    import DMXControl

# Create an instance of the AnalogInputs class to read in the analog values
# from the knobs and switches.
analog_in    = AnalogInputs()

# Create an instance of the DMXControl class that wraps the OLA DMX library.
dmx_control  = DMXControl()

# Instantiate a set of ColorSelector classes. 
#
# We specify the following parameters for each one:
# - Input knob line: The voltage here determines the channel birghtness.
# - Color channel: What DMX channel to control with that knob.
# - DMX control: The DMXControl object to use to update the light.
color_selectors = [
    ColorSelector(0, DMXControl.CHANNEL_RED, dmx_control), 
    ColorSelector(1, DMXControl.CHANNEL_GREEN, dmx_control), 
    ColorSelector(2, DMXControl.CHANNEL_BLUE, dmx_control), 
    ]

# Now we loop forever.
while True:
    # Read in the current values of all of the analog lines.    
    inputs = analog_in.read_values()

    # Iterate across each color selector and tell it to update itself based
    # on the analog line values.
    for channel in color_selectors:
        channel.update_channel_brightness(inputs)
	
