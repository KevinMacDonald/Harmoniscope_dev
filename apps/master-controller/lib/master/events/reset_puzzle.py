# events/reset_puzzle.py - An event to reset the puzzle.

import logging
from master.events import event

class Event(event.Event):
    def __init__(self, when):
        self.when = when

    def type(self):
        return "reset_puzzle"

    def run(self):
        logging.info("Resetting puzzle: randomizing sounds.")
        from master.state_tracker import StateTracker
        from master.system_state import SystemState
        StateTracker.reset_puzzle()
        SystemState.set_state(SystemState.STATE_RUNNING)
        return []