# events/pixel_sequence.py - Set pixels to a given color in sequence, over
#                            the given time period..

import requests
import time

from master.config      import Config
from master.pixel_state import PixelState

from master.events      import event
from master.events      import update_pixel

class Event(event.Event):
    ##
    # Initialize a pixel sequence event.
    #
    # @param when        - The next time at which to update the pixels.
    # @param duration    - How long the sequence should take, in seconds.
    # @param pixel_ids   - A list of lists of pixels to update. Each list
    #                      will be iterated in order, and all pixels in that
    #                      list will be set to the next color in the color list.
    # @param colors      - The list of colors to set the pixels to. The colors
    #                      will be looped through in sequence.
    #
    def __init__(self, when, duration, pixel_ids, colors):
        self.when        = when
        self.stop_time   = when + duration
        self.pixel_ids   = pixel_ids
        self.colors      = colors

        self.step_time   = duration / len(pixel_ids)
        self.pixel_index = 0

    def type(self):
        return "pixel_sequence"

    def run(self):
        new_events = []

        cur_pixel = self.pixel_index
        color = Color(self.colors[cur_pixel % len(self.colors)])

        # If we're past the end time, stop.
        if cur_pixel >= len(self.pixel_ids):
            return new_events

        # Set the next pixels to the desired color.
        event = update_pixel.Event(when      = time.time(),
                                   pixel_ids = self.pixel_ids[cur_pixel], 
                                   color     = color)
        new_events.append(event)
       
        # Advance to the next pixel, and add the next sequence event. 
        self.pixel_index += 1    
        self.when = self.when + self.step_time
        new_events.append(self)

        return new_events

