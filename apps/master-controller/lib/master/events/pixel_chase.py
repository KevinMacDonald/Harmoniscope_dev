# events/pixel_chase.py - Set all of the pixels black, and then move 
#                         the given color along those pixels, over the 
#                         given time period, resetting each pixel to black 
#                         along the way.

import logging
import requests
import time

from master.color       import Color
from master.config      import Config
from master.pixel_state import PixelState

from master.events      import event
from master.events      import update_pixel

class Event(event.Event):
    ##
    # Initialize a pixel chase event.
    #
    # @param when        - The next time at which to update the pixels.
    # @param duration    - How long the pixel chase event should last (seconds).
    # @param pixel_ids   - The IDs of the pixels to update.
    # @param color       - The color value to chase.
    #
    def __init__(self, when, duration, pixel_ids, color):
        self.when        = when
        self.stop_time   = when + duration
        self.pixel_ids   = pixel_ids
        self.color       = Color(color)

        self.step_time   = duration / (len(pixel_ids) + 1)
        self.pixel_index = 0

    def type(self):
        return "pixel_chase"

    def run(self):
        new_events = []

        self.when = self.when + self.step_time

        cur_pixel = self.pixel_index

        # Reset the previous pixel back to its stored color.
        if cur_pixel != 0:
            pixel_number = self.pixel_ids[cur_pixel - 1]
            event = update_pixel.Event(when      = time.time(),
                                       pixel_ids = pixel_number, 
                                       color     = self.cur_color)
            new_events.append(event)

        # If we're past the end time, stop.
        if cur_pixel >= len(self.pixel_ids):
            logging.debug("Stopping at pixel index %d" % cur_pixel)
            return new_events

        # Stash the pixel's current color.
        self.cur_color = PixelState.get(self.pixel_ids[cur_pixel])

        # Set it to the chase color.
        event = update_pixel.Event(when      = time.time(),
                                   pixel_ids = self.pixel_ids[cur_pixel], 
                                   color     = self.color)
        new_events.append(event)
       
        # Advance to the next pixel, and add the next chase event. 
        self.pixel_index += 1    
        new_events.append(self)

        return new_events
