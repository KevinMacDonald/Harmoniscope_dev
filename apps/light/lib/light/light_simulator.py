# ui_simulator.py - A worker that simulates the DMX-controlled lights

# Uses the tkinter library that is included with Python, which is a wrapper
# around Tk, a cross-platform UI library.

import json
import jsmin

from tkinter import *
from queue import Queue, Empty
from light.constants import *

CANVAS_WIDTH  = 800
CANVAS_HEIGHT = 600

# Private utility class to represent a virtual pixel.
class Pixel:
    # The dimensions of the pixel UI representations.
    PIXEL_WIDTH  = 10
    PIXEL_HEIGHT = 10

    # Initialize the pixel, using the specified tkinter Canvas object as the
    # UI parent, passing in an options dict:
    #
    #  id:  The pixel ID number.
    #  x:   The pixel's horizontal position on the canvas.
    #  y:   The pixel's vertical position on the canvas.
    def __init__(self, canvas, options):
        self.id = int(options["id"])
        self.x  = int(options["x"])

        # The Y axis is reversed on the drawings as compared to the screen.
        self.y  = CANVAS_HEIGHT - int(options["y"])

        # We store the set color so that we can do delayed repaints.
        self.cached_color = '#000000'

        # Create the circle representing the pixel.
        self.canvas = canvas
        self.oval = canvas.create_oval(self.x,
                                       self.y,
                                       self.x + self.PIXEL_WIDTH,
                                       self.y + self.PIXEL_HEIGHT,
                                       fill = self.cached_color, 
                                       outline = '#303030')

    # Set the color of this pixel. Does not redraw the pixel.
    def set_color(self, color):
        self.cached_color = color

    # Update the displayed color of this pixel with the cached color value.
    def paint(self):
        if (self.canvas.itemcget(self.oval, "fill") != self.cached_color):
            self.canvas.itemconfigure(self.oval, fill = self.cached_color)

# The LightSimulator class implements a simple TKinter application to visually
# simulate the DMX LED string. This class must be used on the main thread.
class LightSimulator():

    # Create a LightSimulator, using the pixel configuration file specified.
    def __init__(self, config_file):
        self.load_configuration(config_file)

    # Load in the pixel configuration file.
    def load_configuration(self, pixel_config):
        with open(pixel_config) as config_file:
            # Use JSMin to remove the comments in the config file.
            minified = jsmin.jsmin(config_file.read())

            # Parse the JSON into a Python object.
            self.config = json.loads(minified)

    # Setup the simulator UI. Assumes the configuration's already been loaded.
    def setup(self):
        # Create the TKinter root window.
        self.root = Tk()

        # This is a hack to cause the UI to run every 50 milliseconds, so that
        # Ctrl-C in the terminal works as expected.
        self.root.after(1, self.check)

        # Create the queue for update events.
        self.queue = Queue()

        # Bind the event that we use to notify that update events are pending.
        self.root.bind_all('<<Update>>', self.update_pixels_handler)

        # Create a Frame to hold the UI.
        frame = Frame(self.root)
        frame.pack()

        # Create the Canvas that we draw the pixels in.
        self.canvas = Canvas(frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, 
                             background='black')
        self.canvas.grid()

        # Create the quit button.
        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.grid()

        # Create the pixels from the configuration.
        self.pixels = dict()
        for pixel_config in self.config["pixels"]:
            pixel = Pixel(self.canvas, pixel_config)
            self.pixels[pixel.id] = pixel

        # Bring the window to the front. Complex because OSX is odd, but 
        # should be universal.
        self.root.lift()
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.root.after_idle(self.root.call, 'wm', 'attributes', '.', '-topmost', False)

    # Factor the white value into the given color brightness. 
    #
    # The current implementation does nothing if the color is brighter than
    # the white value. If the white value is brighter, it adds half of the 
    # difference to the color value. This is a pretty dumb approach that 
    # probably needs tweaking at some point.
    def adjust_brightness_for_white(self, color_value, white_value):
        if (white_value <= color_value):
            return color_value
        else:
            return int(min(color_value + (white_value - color_value) / 2, 255))

    # Convert an RGBW value in a WorkItem to a RGB value, factoring in the
    # white value..
    def rgb_for_workitem(self, work_item):
        return ( 
            self.adjust_brightness_for_white(work_item.red,   work_item.white),
            self.adjust_brightness_for_white(work_item.green, work_item.white),
            self.adjust_brightness_for_white(work_item.blue,  work_item.white)
            )

    # Set the pixel values based on the given work item.
    def update_pixels(self, work_item):
        self.queue.put(work_item)
        self.root.event_generate('<<Update>>')
        self.root.update_idletasks()

    # An event handler for the update pixels call.
    def update_pixels_handler(self, event):
        try:
            work_item = self.queue.get(False)
        except Empty:
            return

        (r_value, g_value, b_value) = self.rgb_for_workitem(work_item)

        # Pixel value '0' is magic and says set all pixels to the given 
        # color.
        for pixel in work_item.pixels:
            if (pixel == 0):
                for pixel_id in self.pixels:
                    self.set_pixel_color(pixel_id, r_value, g_value, b_value)
                break
            else:
                self.set_pixel_color(pixel, r_value, g_value, b_value)

        # Now repaint, if we've been told to.
        if (work_item.paint != 0):
            for pixel_id in self.pixels:
                self.pixels[pixel_id].paint()

        # If the queue's still not empty, generate another event to process
        # it.
        if not self.queue.empty():
            self.root.event_generate('<<Update>>')

    # Set the given pixel's color to the RGB value.
    def set_pixel_color(self, pixel_id, red, green, blue ):
        color = '#%02x%02x%02x' % (red, green, blue)
        self.pixels[pixel_id].set_color(color)

    # Run the UI main loop, and clean up after it's done.
    def run(self):
        self.setup()
        self.root.mainloop()
        self.root.destroy()

    # The other half of the hack to make Ctrl-C from the terminal window
    # work. Kicks the UI thread every 50ms.
    def check(self):
        self.root.after(1, self.check)

