# events/update-pixel.py - An event to set the value of a pixel.

import logging
import requests

from master.config      import Config
from master.color       import Color
from master.pixel_state import PixelState

from master.events import event

class Event(event.Event):
    ##
    # Initialize a pixel update event.
    #
    # @param when      - The time at which to update the pixel.
    # @param pixel_ids - The IDs of the pixels to update.
    # @param color     - The color value to set.
    # @param paint     - Set to True to indicate that the pixels should be
    #                    painted out. (Default to True)
    #
    def __init__(self, when, pixel_ids, color, paint = True):
        self.when     = when
        self.color    = color

        if type(pixel_ids) is not list:
            self.pixels = [pixel_ids]
        else:
            self.pixels = pixel_ids

        if paint:
            self.paint = 1
        else:
            self.paint = 0

        self.base_url = "http://" + Config.get("light-server") + ":8000/light/"

    def type(self):
        return "update_pixel"

    def run(self):
        pixel_string = ",".join(map(str, self.pixels))
        url = self.base_url + pixel_string

        params = { 
            'r': int(self.color.red),
            'g': int(self.color.green),
            'b': int(self.color.blue),
            'w': int(self.color.white),
            'p': self.paint
            }

        logging.debug("Setting pixels %s to: %d, %d, %d" % (
                        pixel_string,
                        params['r'],
                        params['g'],
                        params['b']))

        try:
            # Send the change request to the light server.
            response = requests.get(url, params = params)

            # Update our internal pixel state.
            for pixel in self.pixels:
                PixelState.set(pixel, self.color)

        except requests.exceptions.RequestException as error:
            print("Error sending update to light service:", error) 
        
