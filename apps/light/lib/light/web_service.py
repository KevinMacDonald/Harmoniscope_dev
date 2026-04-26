# web_service.py - The light server web service.

# Implements a RESTful web service using the Flask framework, running in an
# independent thread. Passes light state changes to a Worker thread using
# WorkItem instances in a queue.

import logging
import sys
import os.path

from flask import Flask, request, abort
from threading import Thread

from light.constants import *
from light.workitem  import WorkItem

class WebService(Thread):
    # Initialize the thread and create the Flask server instance. Pass in the
    # Worker instance that will handle light state change work items.
    def __init__(self, worker):
        # Initialize the thread and set it to be a 'daemon', so that we won't
        # keep the process from exiting if the main thread dies.
        Thread.__init__(self)
        self.daemon = True

        # Create the Flask app, and set up the request routing.
        self.app = Flask(__name__)
        self.app.add_url_rule('/light/<pixels_string>', 
                              'set_pixel', self.set_pixel)

        # Stash the worker instance.
        self.worker = worker

    # Thread body, runs the Flask server instance.
    def run(self):
        self.app.run(debug        = False, 
                     host         = '0.0.0.0', 
                     port         = 8000, 
                     use_reloader = False, 
                     threaded     = False,
                     use_debugger = False)

    #########################################################################
    #
    # Helper functions
    #
    #########################################################################

    ##
    # This function validates that the pixel number given is within 
    # bounds, returning True if so, False if not.
    def is_pixel_value_sane(self, pixel_value):
        p = int(pixel_value)

        # 0 is valid because it is the "wildcard" value.
        if (p >= 0 and p <= MAX_PIXEL):
            return True
        else:
            return False 

    ##
    # This function will ensure that the value for a channel is within bounds.
    def sanitize_brightness_value(self, brightness_value):
        if (brightness_value > MAX_BRIGHTNESS):
            return (MAX_BRIGHTNESS)
        elif (brightness_value < 0):
            return 0
        else:
            return brightness_value

    ############################################################################
    #
    # Main dispatcher routine
    #
    ############################################################################

    ##
    # This function will receive the instructins to set a particular pixel
    # to a set of given R,G,B,W values and queue it up to the DMX processor 
    #
    # @param <pixel> - a comma separated list of the addresses of the pixel to modify (0 for all)
    # @param <brightnessValues> - a list of R,G,B,W values e.g. 1,2,3,4
    # @param <paint ('p') value> - defaults to 1; if 0, values are cached but not immediately painted 
    #
    # Restful API call examples:
    #     http://192.168.8.116:8000/light/0?r=0&g=0&b=0&w=0 - turns everything off
    #     http://192.168.8.116:8000/light/1?r=255&g=0&b=0&w=0&p=0 - turns first pixel to red but does not repaint the scene
    #     http://192.168.8.116:8000/light/2?r=0&g=255&b=0&w=0 - turns second pixel to green and repains the scene
    #     http://192.168.8.116:8000/light/2,3?r=0&g=255&b=0&w=0 - turns second and third pixel to green and repains the scene
    #
    def set_pixel(self, pixels_string):
        pixels = list(map(int, pixels_string.split(",")))

        # Only accept inputs for valid 'pixel' values
        for pixel in pixels:
            if (self.is_pixel_value_sane(pixel) == False):
                abort(400, "Invalid pixel ID value %d" % pixel)

        # Extract and sanitize brightness values
        r_value = self.sanitize_brightness_value(request.args.get('r',0,type=int))
        g_value = self.sanitize_brightness_value(request.args.get('g',0,type=int))
        b_value = self.sanitize_brightness_value(request.args.get('b',0,type=int))
        w_value = self.sanitize_brightness_value(request.args.get('w',0,type=int))
        p_value = request.args.get('p',1,type=int)

        # Queue up a work item to the consumer thread
        work_item = WorkItem(pixels, r_value, g_value, b_value, w_value, p_value)
        self.worker.queue_work_item(work_item)

        output = "Input for pixel {}: r={},g={},b={},w={},p={}".format(pixels_string, r_value, g_value, b_value, w_value, p_value)
        logging.info(output)

        return output

