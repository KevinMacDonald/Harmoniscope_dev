# events/pixel_flash.py - An event to flash a set of pixels to a color.

import logging
import requests
import time

from master.constants   import *
from master.config      import Config
from master.color       import Color
from master.pixel_state import PixelState

from master.events      import event
from master.events      import update_pixel

class Event(event.Event):
    ##
    # Initialize a pixel flash event.
    #
    # @param when      - The time at which to update the pixel.
    # @param pixel_ids - A list of the IDs of the pixels to flash.
    # @param color     - The color value to set.
    # @param period    - The time between flashes (in seconds).
    # @param ratio     - The ratio of flash to normal color (between 0 and 1).
    # @param count     - The number of times to flash, or None to flash forever.
    #
    def __init__(self, when, pixel_ids, color, period, ratio, count = None):
        # Copy the parameters in.
        self.when      = when
        self.pixel_ids = pixel_ids
        self.color     = color
        self.period    = period
        self.ratio     = ratio

        # Set our state variables.
        self.is_flashed = False
        self.stop       = False
        self.remaining  = count
        self.old_colors = {}

    def type(self):
        return "pixel_flash"

    def run(self):
        new_events = []

        # If we've been told to stop, then stop.
        if self.stop:
            logging.debug("Stopping hint: %s", self.stop)
            return new_events

        # If we're currently flashing the color, revert to the old color
        # and swap our state.
        if self.is_flashed:
            self.is_flashed = False

            # Reset the pixels back to their original color.
            for id in self.pixel_ids:
                event = update_pixel.Event(
                                     when      = time.time(),
                                     pixel_ids = [ id ],
                                     color     = self.old_colors[id])
                new_events.append(event)

            # If there are any remaining flashes, set the new flash after the
            # rest of the flash interval.
            self.when = time.time() + (self.period * (1 - self.ratio))

            # If there's no value, then we run forever. This won't be zero
            # because we check immediately after decrementing below.
            if not self.remaining:
                new_events.append(self)

            # Otherwise decrement the counter and see if there are any flashes
            # left.
            else: 
                self.remaining -= 1
                if self.remaining > 0:
                    new_events.append(self)

        # Otherwise, flash to the color. 
        else:
            self.is_flashed = True

            # Cache the old pixel color.
            for id in self.pixel_ids:
                self.old_colors[id] = Color(PixelState.get(id))

            # Set the pixels to the flash color.
            event = update_pixel.Event(
                                    when      = time.time(),
                                    pixel_ids = self.pixel_ids,
                                    color     = Color(self.color))
            new_events.append(event)
       
            # Set ourselves to reset the pixels after the flash ratio passes.
            self.when = time.time() + (self.period * self.ratio)
            new_events.append(self)

        return new_events

    def stop_hint(self):
        logging.debug("Hint told to stop")
        self.stop = True 

