# dmx.py - A module for controlling DMX output

# DMXControl provides a set of methods for controlling the DMX output 
# to the lights
#
# Depends on ola-python: http:// opendmx.net/index.php/OLA_Python_API

import array
import logging

from ola.ClientWrapper import ClientWrapper
from light.workitem    import WorkItem

class DMXControl:
    # The DMX 'universe' that we want to use. In OLA, we wire up a DMX universe
    # of up to 512 channels to a DMX interface. We use the default of 1.
    DEFAULT_UNIVERSE = 1

    # There are four channels per pixel - Red, Green, Blue and White
    CHANNELS_PER_PIXEL = 4

    # Initialize the DMX controller. Pass in the number of pixels attached
    # to the DMX bus, and the DMX universe to use.
    def __init__(self, pixel_count, universe = DEFAULT_UNIVERSE):
        self.universe    = universe
        self.pixel_count = pixel_count
        self.initialized = False

    # Initialize the OLA wrapper. We don't do this in the __init__ method
    # because we have to do it in the same thread that we do the OLA 
    # operations in.
    def initialize(self):
        if self.initialized:
            return

        self.initialized = True

        # Initialize the OLA client wrapper.
        self.wrapper    = ClientWrapper()
        self.client     = self.wrapper.Client()

        # Create the array to cache the brightness values for each pixel
        # channel.
        self.channels = array.array('B')
        for i in range(self.pixel_count * self.CHANNELS_PER_PIXEL):
            self.channels.append(0)

    # Set the brightness of a given pixel.
    def set_pixel_values(self, pixel, red, green, blue, white):
        assert(pixel > 0)

        # Calculate the base channel for the pixel.
        base_channel = (pixel - 1) * self.CHANNELS_PER_PIXEL

        self.channels[base_channel+0] = red
        self.channels[base_channel+1] = green
        self.channels[base_channel+2] = blue
        self.channels[base_channel+3] = white

    # Set the birghtness of a given pixel (or every pixel) based on work item.
    def update_pixels(self, work_item):
        self.initialize()

        for pixel in work_item.pixels:
            logging.debug("Updating pixel %d", pixel)
            self.update_pixel(pixel, 
                              work_item.red, 
                              work_item.green, 
                              work_item.blue, 
                              work_item.white)

        # Send the output to DMX if work item has "paint" flag set.
        if (work_item.paint != 0):
            self.client.SendDmx(self.universe, self.channels, self.dmx_sent)
            self.wrapper.Run()

    def update_pixel(self, pixel, red, green, blue, white):
        # Set the four channels (R/G/B/W) base on work item data
        if (pixel == 0):
            # For wildcard pixel, address all pixels
            min_pixel = 1
            max_pixel = self.pixel_count + 1 # Unreachable max
        else:
            # For a single pixel, set only its channels
            min_pixel = pixel
            max_pixel = min_pixel + 1 # Unreachable max

        # Now iterate over the computed channel range and set the 
        # brightness values.
        for id in range(min_pixel, max_pixel):
            self.set_pixel_values(id, red, green, blue, white)

    # This function gets called back when the DMX message has been sent.
    def dmx_sent(self, state):
        self.wrapper.Stop()

