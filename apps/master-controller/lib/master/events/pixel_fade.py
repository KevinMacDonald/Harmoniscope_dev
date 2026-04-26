# events/pixel_fade.py - An event to fade a set of pixels from one color to
#                        another.

import copy
import logging
import requests
import time

from master.color  import Color
from master.config import Config

from master.events import event
from master.events import update_pixel

class Event(event.Event):
    ##
    # Initialize a pixel fade event.
    #
    # @param when        - The next time at which to update the pixels.
    # @param duration    - How long the fade should take (in seconds).
    # @param steps       - The number of steps in which to perform the fade.
    # @param pixel_ids   - The IDs of the pixels to update.
    # @param start_color - The color value to start the fade at.
    # @param end_color   - The color value to finish the fade at.
    #
    def __init__(self, when, duration, steps, pixel_ids, start_color, end_color):
        self.when        = when
        self.stop_time   = when + duration
        self.steps       = steps
        self.pixel_ids   = pixel_ids
        self.start_color = Color(start_color)
        self.end_color   = Color(end_color)

        self.step_time   = duration / steps

        self.color_step  = Color({
            "red":      (self.end_color.red   - self.start_color.red)/steps,
            "green":    (self.end_color.green - self.start_color.green)/steps,
            "blue":     (self.end_color.blue  - self.start_color.blue)/steps,
            "white":    (self.end_color.white - self.start_color.white)/steps
            })
        logging.debug("Color step: %d, %d, %d" % (self.color_step.red, self.color_step.green, self.color_step.blue))

        self.cur_color = Color(start_color)

    def type(self):
        return "pixel_fade"

    def run(self):
        new_events = []

        self.when = self.when + self.step_time

        # If we're past the end time, make sure we land on the final color.
        if self.when >= self.stop_time:
            self.cur_color = self.end_color

        # We're not past the end time, so add ourselves back on the event queue.
        else:
            new_events.append(self)

        event = update_pixel.Event(when      = time.time(),
                                   pixel_ids = self.pixel_ids, 
                                   color     = copy.copy(self.cur_color)) 
        new_events.append(event)
           
        self.cur_color.add(self.color_step)
        logging.debug("Cur color: %d, %d, %d" % (self.cur_color.red, self.cur_color.green, self.cur_color.blue))

        return new_events
