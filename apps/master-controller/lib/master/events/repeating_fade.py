# events/repeating_fade.py - An event to repeatedly fade in and out a set of 
#                            pixels.

import requests
import time

from master.config       import Config
from master.color        import Color
from master.system_state import SystemState
from master.pixel_state  import PixelState

from master.events       import event
from master.events       import pixel_fade 

class Event(event.Event):
    # Constants to represent whether we're fading in (brightening) or fading 
    # out (darkening) the pixels.
    FADE_IN  = 1
    FADE_OUT = 2

    ##
    # Initialize a repeating fade event.
    #
    # @param when      - The time at which to update the pixel.
    # @param pixel_ids - A list of the pixel IDs to fade.
    # @param period    - The time (in seconds) for each fade.
    # @param steps     - The number of steps to take for each fade.
    #
    def __init__(self, when, pixel_ids, period, steps):
        self.when      = when
        self.pixel_ids = pixel_ids
        self.period    = period
        self.steps     = steps
    
        self.direction = self.FADE_IN

    def type(self):
        return "repeating_fade"

    def run(self):
        new_events = []

        if self.direction == self.FADE_IN:
            self.direction = self.FADE_OUT
            start_color    = Color.from_html("#ffffff")
            end_color      = Color.from_html("#000000")

        else:
            self.direction = self.FADE_IN
            start_color    = Color.from_html("#000000")
            end_color      = Color.from_html("#ffffff")

        event = pixel_fade.Event(when        = time.time(),
                                 duration    = self.period,
                                 steps       = self.steps,
                                 pixel_ids   = self.pixel_ids, 
                                 start_color = start_color,
                                 end_color   = end_color)
        new_events.append(event)

        self.when = self.when + self.period
        new_events.append(self)

        return new_events                
        
