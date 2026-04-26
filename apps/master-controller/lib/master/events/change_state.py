# events/change_state.py - An event to change the Harmoniscope's state.

import requests
import time

from master.config        import Config
from master.constants     import *
from master.event_queue   import EventWorker
from master.system_state  import SystemState

from master.events        import event
from master.events        import load_event_script

class Event(event.Event):
    ##
    # Initialize a start main event event.
    #
    # @param when      - The time at which to update the pixel.
    # @param new_state - The new state to set.
    #
    def __init__(self, when, new_state):
        self.when      = when
        self.new_state = new_state

        if self.new_state > SystemState.MAX_STATE or self.new_state < SystemState.MIN_STATE:
            raise ValueError("Invalid system state %d" % self.new_state)

    def type(self):
        return "change_state"

    def run(self):
        new_events = []

        # If we're already in the new state, do nothing.
        if SystemState.get_state() == self.new_state:
            return new_events

        # Create a single event to load the script for the given state.
        script_file = EVENT_SCRIPT_MAPPING[self.new_state]
        event = load_event_script.Event(when        = time.time(),
                                        script_file = script_file)
        new_events.append(event)

        # Delete all of the current events.
        EventWorker.replace_queue([])

        # Update the system state.
        SystemState.set_state(self.new_state)

        return new_events                
        
