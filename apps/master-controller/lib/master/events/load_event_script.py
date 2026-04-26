# events/load_event_script.py - An event to load a script of events.

import logging
import time
import json
import jsmin

from master.config       import Config
from master.color        import Color
from master.system_state import SystemState
from master.pixel_state  import PixelState

import master.events

from master.events        import event

class Event(event.Event):
    ##
    # Initialize a load event script event.
    #
    # @param when        - The time at which to start events in the script.
    # @param script_file - The file to load the script from.
    #
    def __init__(self, when, script_file):
        self.when        = when
        self.script_file = Config.get('event-scripts') + '/' + script_file

    def type(self):
        return "load_event_script"

    def run(self):
        new_events = []

        with open(self.script_file) as config_file:
            # Use JSMin to remove the comments in the config file.
            minified = jsmin.jsmin(config_file.read())

            # Parse the JSON into a Python object.
            script = json.loads(minified)

            # Iterate across the input events.
            for input_event in script["events"]:
                # Adjust the time to be offset from now.
                input_event['when'] += time.time()

                # Get the type from the config.
                type = input_event.pop('type')

                # Create the event.
                try:
                    event_class = Event._get_class_for_type(type)
                    event = event_class(**input_event)
                    new_events.append(event)

                except Exception as e:
                    logging.exception("Invalid event type %s in script" % type, e)

        return new_events                
      
    def _get_class_for_type(type_name):
        class_name = "master.events." + type_name + ".Event"

        parts = class_name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)

        for comp in parts[1:]:
            m = getattr(m, comp)            

        return m
     
