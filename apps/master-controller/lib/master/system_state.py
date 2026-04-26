# system_state.py - Overall system state tracker. Keeps track of whether the
#                   main event is being run or not.

import time

class SystemState:
    STATE_RUNNING    = 1
    STATE_MAIN_EVENT = 2

    MAX_STATE = 2
    MIN_STATE = 1

    current_state    = -1
    state_entry_time = time.time()

    def get_state():
        return SystemState.current_state

    def get_state_entry_time():
        return SystemState.state_entry_time

    def set_state(new_state):
        SystemState.current_state    = new_state
        SystemState.state_entry_time = time.time()


