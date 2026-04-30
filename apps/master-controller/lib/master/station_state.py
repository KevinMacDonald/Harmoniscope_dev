# station_state.py - Track an individual station's state.

import logging
import time
import random
import copy
import threading

from master.constants    import *
from master.config       import Config
from master.color        import Color
from master.system_state import SystemState

from master.events       import pixel_flash
from master.events       import play_note
from master.events       import play_sound
from master.events       import stop_note
from master.events       import update_pixel

class StationState:
    ##
    # Initialize the station state from the given station config dictionary.
    def __init__(self, station_id, station_config):
        self.id               = station_id
        self.station_config   = station_config
        self.last_update_time = 0
        self.lock             = threading.Lock()

        if 'instrument' not in station_config:
            station_config['instrument'] = DEFAULT_MIDI_INSTRUMENT
    
        if 'velocity' not in station_config:
            station_config['note_velocity'] = DEFAULT_NOTE_VELOCITY

        self.knobs = {}
        for knob_id_str in station_config['knobs']:
            # Create a deep copy of the knob's configuration data to ensure this
            # station's state is fully independent and prevent shared state issues.
            knob_config = copy.deepcopy(station_config['knobs'][knob_id_str])

            # Initialize the runtime state for this knob.
            knob_config['current_value'] = 0
            knob_config['last_update']   = 0
            knob_config['hint']          = None

            self.knobs[int(knob_id_str)] = knob_config
            
        self.randomize_sounds()


    def randomize_sounds(self):
        """Randomize the sound mappings for each knob to create the puzzle."""
        with self.lock:
            logging.info("Randomizing puzzle sounds for station %d...", self.id)
            for id, knob in self.knobs.items():
                if 'sounds' in knob:
                    shuffled_sounds = list(knob['sounds'])
                    random.shuffle(shuffled_sounds)
                    knob['randomized_sounds'] = shuffled_sounds
                    
                    # Find the new target position where the 'stationzap' sound is located
                    for i, sound in enumerate(shuffled_sounds):
                        logging.info("Knob %d position %d assigned sound: %s", id, i + 1, sound)
                        if sound.startswith("stationzap"):
                            knob['target_position'] = i
                    
                    logging.info("Knob %d target position is now %d ('%s')", id, knob['target_position'] + 1, shuffled_sounds[knob['target_position']])

    ##
    # Update the station's values.
    def update(self, analog_inputs):
        with self.lock:
            new_events = []
            for id in self.knobs:
                # Ignore 0 values. Since the hardware conversion to digital, 0 indicates
                # a switch between detents (deadzone). We retain the last valid position.
                if analog_inputs[id - 1] == 0:
                    continue

                knob = self.knobs[id]

                # The analog inputs array is zero-indexed, the knob numbers are
                # indexed starting at 1.
                new_position = self._analog_value_to_position(analog_inputs[id - 1], id)
       
                # If the knob position hasn't changed, go to the next knob.
                if (new_position == knob['current_value']):
                    continue

                # Set the last update time for the knob, so we know if it's
                # been moved since the main event.
                knob['last_update'] = time.time()

                # Change the pixel to match the new position. 
                # new_color = self.get_color(id, new_position)
                # event = update_pixel.Event(
                #                 when      = time.time(), 
                #                 pixel_ids = [ self.get_pixel(id) ], 
                #                 color     = new_color)
                # new_events.append(event)

                # (Legacy visual and audio hint logic has been removed for standalone operation)
                    
                # Play the sound associated with the new position instead of a MIDI note.
                # This assumes the 'notes' array in your config maps to the names of your .wav files.
                event = play_sound.Event(
                                 when       = time.time(), 
                                 station_id = self.id, 
                                 sound      = str(self.get_sound(id, new_position)))
                new_events.append(event)
                   
                knob['current_value'] = new_position

            self.last_update_time = time.time()

            return new_events

    ##
    # Get the target position for the knob on this station.
    def get_target_position(self, knob):
        return self.knobs[knob]['target_position']

    ##
    # Get the name of the sound hint for the knob on this station.
    def get_sound_hint(self, knob):
        return self.knobs[knob]['sound_hint']

    ##
    # Get the pixel that maps to the knob on this station.
    def get_pixel(self, knob):
        return self.knobs[knob]['pixel']

    ##
    # Get the color for the given knob position. If no position is specified,
    # returns the color for the current knob position.
    def get_color(self, knob, position = None):
        if position is None:
            position = self.knobs[knob]['current_value']

        return Color.from_html(self.knobs[knob]['colors'][position])

    ##
    # Get the note for the given knob position. If no position is specified,
    # returns the note for the current knob position.
    def get_note(self, knob, position = None):
        if position is None:
            position = self.knobs[knob]['current_value']

        return self.knobs[knob]['notes'][position]

    ##
    # Get the sound for the given knob position. If no position is specified,
    # returns the sound for the current knob position.
    def get_sound(self, knob, position = None):
        if position is None:
            position = self.knobs[knob]['current_value']

        # The config should have a 'sounds' array with the names of the .wav files.
        if 'randomized_sounds' in self.knobs[knob]:
            return self.knobs[knob]['randomized_sounds'][position]
        elif 'sounds' not in self.knobs[knob]:
            logging.warning("Knob %d config is missing 'sounds' array. Using 'notes' as fallback.", knob)
            return self.get_note(knob, position)
        return self.knobs[knob]['sounds'][position]

    ##
    # Returns true if this station's main event condition is satisfied.
    def is_main_event_met(self):
        with self.lock:
            # Iterate across all of the knobs, and if any of them don't match,
            # then we haven't met the condition.
            for id in self.knobs:
                knob = self.knobs[id]

                # If the current value doesn't match the target position, then
                # we haven't met the criteria.
                if knob['current_value'] != knob['target_position']:
                    logging.debug("Station %d Knob %d failed: current %d != target %d", self.id, id, knob['current_value'] + 1, knob['target_position'] + 1)
                    return False

            # Everyone matches, this station is all set.
            return True

    #
    # Translate an analog input value to a knob position.
    def _analog_value_to_position(self, analog_value, knob_id=None):
        # Handle digital IO Pi board input (values 1-8 from control-scan)
        # The IO Pi reads which pin is HIGH on the multiplexer, returning 1-8
        if 1 <= analog_value <= KNOB_POSITION_COUNT:
            position = int(analog_value) - 1
            
            # Apply software unscrambling if hardware wires are crossed
            if knob_id and knob_id in self.knobs and 'wire_correction' in self.knobs[knob_id]:
                correction_map = self.knobs[knob_id]['wire_correction']
                # JSON keys are strings, so convert pin number to string
                pin_str = str(int(analog_value))
                if pin_str in correction_map:
                    position = int(correction_map[pin_str]) - 1
                    
            return position

        # Handle original analog ADC input (voltage 0-5V)
        # This preserves backward compatibility with the original hardware
        position = int((analog_value / MAX_KNOB_VOLTAGE) * KNOB_POSITION_COUNT)
        position = max(position, 0)
        position = min(position, KNOB_POSITION_COUNT - 1)
        return position
