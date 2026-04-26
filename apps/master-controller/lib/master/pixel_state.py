# pixel_state.py - Tracks the current colors of the pixels.

from master.constants import *
from master.color     import Color

class PixelState:
    pixels = list()

    def get(pixel_id):
        try:
            return PixelState.pixels[pixel_id]

        except KeyError as error:
            return Color()

    def set(pixel_id, color):
        # Special case: 0 means set all pixels.
        if pixel_id == 0:
            for i in range(1, MAX_PIXELS):
                PixelState.set(i, color)
            return

        # If it's out of range (and pixels are 1-indexed), ignore it.
        if (pixel_id < 1) or (pixel_id > MAX_PIXELS):
            return

        # If it's beyond our current list of pixels, extend the list.
        if pixel_id >= len(PixelState.pixels):
            for i in range(len(PixelState.pixels), pixel_id + 1):
                PixelState.pixels.append(Color())

        # Set the pixel color.
        PixelState.pixels[pixel_id] = color

# Initialize all pixels to black.
PixelState.set(0, Color.from_html("#000000"))

