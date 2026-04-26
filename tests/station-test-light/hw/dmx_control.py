# dmx_control.py - A module for controlling DMX output

# DMXControl provides a set of methods for controlling the DMX output to
# the lights.
#
# Depends on ola-python: http://opendmx.net/index.php/OLA_Python_API

import array
from ola.ClientWrapper import ClientWrapper

class DMXControl:
    # The DMX 'universe' that we want to use. In OLA, we wire up a DMX universe
    # of up to 512 channels to a DMX interface. We use the default of 1.
    DEFAULT_UNIVERSE = 1 

    # For the test app, the DMX interface is connected to a single DMX can light
    # that has three colors. The DMX channels are:
    #
    #  1 - Red channel
    #  2 - Green channel
    #  3 - Blue channel
    #  4 - White channel
    #
    # For this lamp, it appears that if you output just 1 channel, then it 
    # sets a white level. If you output 4 channels, it ignores the first one, 
    # and sets the RGB levels from the next three. If you output 5 channel 
    # values, it enters color cycle mode, at a rate specified by the 5th 
    # channel value.

    CHANNEL_RED   = 0
    CHANNEL_GREEN = 1
    CHANNEL_BLUE  = 2
    CHANNEL_WHITE = 3
    CHANNEL_MAX   = CHANNEL_WHITE

    # Create a new DMX control instance. Specify the universe you wish to use.
    def __init__(self, universe = DEFAULT_UNIVERSE):
        # Set the requested universe.
        self.universe = universe

        # Reset the color array.
        self.color = array.array('B', [0, 0, 0, 0, 0])

        # Create a new DMX client wrapper.
        self.wrapper = ClientWrapper()
        self.client = self.wrapper.Client()

    # Set the brightness of a given channel.
    def set_brightness(self, channel, value):
        if (channel > self.CHANNEL_MAX):
            return
            
        self.color[channel] = value
        self.client.SendDmx(self.universe, self.color, self.dmx_sent)
        self.wrapper.Run()

    # This function gets called back when the DMX message has been sent.
    def dmx_sent(self, state):
        self.wrapper.Stop()
