# events/refresh_stations.py - An event to rewrite all of the stations with
#                              their appropriate lights and sounds.

import requests
import time

from master.config        import Config
from master.color         import Color
from master.state_tracker import StateTracker
from master.events import event

class Event(event.Event):
    ##
    # Initialize a refresh stations event.
    #
    # @param when     - The time at which to initiate the refresh.
    #
    def __init__(self, when):
        self.when    = when

    def type(self):
        return "refresh_stations"

    def run(self):
        new_events = []

        # Get the events to write out the current knob state.
        new_events = StateTracker.get_refresh_events()

        return new_events                
        
