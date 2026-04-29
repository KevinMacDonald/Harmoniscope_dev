# state_tracker.py - Tracks the overall state of the Harmoniscope.

import json
import jsmin
import logging

from master.config        import Config
from master.station_state import *
from master.system_state  import SystemState
from master.event_queue   import EventWorker
from master.events        import play_sound
from master.events        import update_pixel
from master.events        import load_event_script
from master.events        import reset_puzzle

class StateTracker:
    ##
    # The singleton state tracking instance.
    __stations = None

    ##
    # Initialize the state tracker.
    #
    def initialize():
        # If we've already been initialized, don't do anything.
        if StateTracker.__stations:
            return

        if not Config.get('station-config'):
            raise Exception('No station config found.')
      
        # Load the station configuration and create state objects for
        # each station. 
        config_file    = Config.get('station-config')
        station_config = StateTracker._load_station_config(config_file)
        StateTracker.__stations = {}
        for id in station_config["stations"]:
            station = station_config["stations"][id]
            id = int(id)
            StateTracker.__stations[id] = StationState(id, station)

    ##
    # Handle a station update message.
    #
    def update_state(update):
        # Update the station state object, and get any events that need to
        # be run as a result of the update.
        events = StateTracker.__stations[update.station_id].update(update.analog_values)
        logging.debug("Got %d new events", len(events))

        # If the main event is running, then ignore the new events.
        if SystemState.get_state() == SystemState.STATE_MAIN_EVENT:
            return

        # If the main event condition is met, trigger the main event and
        # ignore the events from the update.
        if (StateTracker._is_main_event_triggered() == True):
            logging.info("Main event triggered!")
            logging.info("Puzzle sequence complete! Queueing victory sounds.")
            SystemState.set_state(SystemState.STATE_MAIN_EVENT)
            
            now = time.time()
            station_id = next(iter(StateTracker.__stations.keys()))
            event1 = play_sound.Event(when = now, station_id = station_id, sound = "arrival_processed")
            event2 = play_sound.Event(when = now + 4.0, station_id = station_id, sound = "maineventstations")
            event3 = reset_puzzle.Event(when = now + 38.0)
            
            EventWorker.replace_queue([event1, event2, event3])
            return
            
        # No main event, Queue the update events
        EventWorker.queue_events(events)
        

    ##
    # Get the events necessary to refresh all of the stations to their current
    # state.
    #
    def get_refresh_events():
        # Get the events to play the current sound for every knob on startup.
        return StateTracker.get_startup_sound_events()

    def get_startup_sound_events():
        """Gets the events to play the current sound for every knob."""
        new_events = []
        for id in StateTracker.__stations:
            station = StateTracker.__stations[id]
            for knob in range(1, KNOB_COUNT + 1):
                event = play_sound.Event(
                           when       = time.time(), 
                           station_id = station.id, 
                           sound      = str(station.get_sound(knob)))
                new_events.append(event)
        return new_events

    def reset_puzzle():
        for id in StateTracker.__stations:
            StateTracker.__stations[id].randomize_sounds()

    #
    # Load the station configuration.
    #
    def _load_station_config(station_config):
        with open(station_config) as config_file:
            # Use JSMin to remove the comments in the config file.
            minified = jsmin.jsmin(config_file.read())

            # Parse the JSON into a Python object.
            return json.loads(minified)

    #
    # Test to see if we should trigger the main event.
    #
    def _is_main_event_triggered():
        # Iterate across each station, and if any haven't met the main
        # event condition, then we can't trigger the main event.
        for id, station in StateTracker.__stations.items():
            if (station.is_main_event_met() == False):
                return False

        # All stations meet the condition, fire the main event.
        return True
            
        
