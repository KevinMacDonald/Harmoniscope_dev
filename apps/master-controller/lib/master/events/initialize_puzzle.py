# events/initialize_puzzle.py - An event to set up the puzzle on startup.

import logging
from master.events import event

class Event(event.Event):
    def __init__(self, when):
        self.when = when

    def type(self):
        return "initialize_puzzle"

    def run(self):
        logging.info("Initializing puzzle sound assignments on startup.")
        from master.state_tracker import StateTracker
        
        # This will perform the randomization and log the new assignments.
        StateTracker.reset_puzzle() 
        
        # Now, get the startup sound events and return them to be queued.
        return StateTracker.get_startup_sound_events()