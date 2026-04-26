# events/pixel_sparkle.py - Randomly flash the given pixels full white 
#                           for a brief period.

import requests
import time

from master.config      import Config
from master.pixel_state import PixelState

from master.events      import event
from master.events      import update_pixel

class Event(event.Event):
    ##
    # Initialize a pixel sparkle event.
    #
    # @param when        - The time to start sparkling.
    # @param duration    - How long to sparkle for, in seconds.
    # @param pixel_ids   - The IDs of the pixels to update.
    # @param flash_rate  - The maximum delay between random flashes.
    #
    def __init__(self, when, duration, pixel_ids, flash_rate):
        self.when        = when
        self.stop_time   = when + stop_time
        self.pixel_ids   = pixel_ids
        self.flash_rate  = flash_rate

        self.pixel_index = 0

    def type(self):
        return "pixel_sparkle"

    def run(self):
        new_events = []

        # Reset the current pixel back to it's stored color.
        cur_pixel = self.pixel_index
        if cur_pixel != 0:
            pixel_number = self.pixel_ids[cur_pixel - 1]
            event = update_pixel.Event(when      = time.time(),
                                       pixel_ids = pixel_number, 
                                       color     = self.cur_color)
            new_events.append(event)

        # If we're past the end time, return.
        if time.time() >= self.stop_time:
            return new_events

        # Figure out what the next pixel we want to flash is.
        cur_pixel = randint(1, len(self.pixel_ids))
        self.pixel_index = cur_pixel
        pixel_number = self.pixel_ids[cur_pixel - 1]

        # Stash the pixel's current color.
        self.cur_color = PixelState.get(self.pixel_ids[cur_pixel])

        # Copy the current color, and set it to white.
        new_color = Color(cur_color)
        new_color.white = 255

        event = update_pixel.Event(when      = time.time(),
                                   pixel_ids = pixel_number, 
                                   color     = new_color)
        new_events.append(event)

        # Advance time.
        self.when += random() * self.flash_rate
        new_events.append(self)

        return new_events
