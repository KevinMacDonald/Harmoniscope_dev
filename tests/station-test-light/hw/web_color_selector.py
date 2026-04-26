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
    def __init__(self, color_channel, dmx_control):
        # Copy the parameters to the instance.            
        self.color_channel   = color_channel
        self.dmx_control     = dmx_control

    # Update the channel brightness based on the list of analog input values.
    def update_channel_brightness(self, value):
        # Sanitize the value
        if value < 0:
            value = 0
        elif value > self.MAX_BRIGHTNESS:
            value = self.MAX_BRIGHTNESS
        else:
            pass # do nothing, value is good

        # Update the brightness of the channel.
        self.dmx_control.set_brightness(self.color_channel, value)
