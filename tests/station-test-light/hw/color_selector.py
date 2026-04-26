# Class to manage selecting the brightness of a color channel for a given knob.
#
# Create an instance of this class for each knob you have. When you create it,
# you specify the channel that the knob controls, and the input line you use 
# to control that channel's brightness.
#
# Once you've got an instance, you can then read in the analog values using the
# AnalogInput class, and pass the array of input analog values to the 
# update_channel_brightness() method to have it select the appropriate note.

class ColorSelector:
    # The maximum brightness value for a channel.
    MAX_BRIGHTNESS = 255

    # Construct a ColorSelector instance. You need to pass in the line numbers
    # for brightness, the color channel and a DMXControl instance to
    # allow the instance to update the light.
    def __init__(self, selection_line, color_channel, dmx_control):
        # Copy the parameters to the instance.
        self.selection_line  = selection_line            
        self.color_channel   = color_channel
        self.dmx_control     = dmx_control

    # Update the channel brightness based on the list of analog input values.
    def update_channel_brightness(self, analog_values):
        # Get the voltage of the selection input.
        selection_voltage = analog_values[self.selection_line]

        # If it's a negative voltage, bump it up to zero. This can happen
        # if there's noise in the analog conversion.
        if selection_voltage < 0:
            selection_voltage = 0

        # Calculate the new note value by converting the voltage into an
        # offset note count, and adding it to the base note value.
        brightness = int(round(selection_voltage / (5.0 / self.MAX_BRIGHTNESS)))

        # Update the brightness of the channel.
        self.dmx_control.set_brightness(self.color_channel, brightness)
