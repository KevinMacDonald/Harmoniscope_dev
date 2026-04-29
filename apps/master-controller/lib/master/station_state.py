# station_state.py - Track an individual station's state.

import logging
import time
import random

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

        if 'instrument' not in station_config:
            station_config['instrument'] = DEFAULT_MIDI_INSTRUMENT
    
        if 'velocity' not in station_config:
            station_config['note_velocity'] = DEFAULT_NOTE_VELOCITY

        self.knobs = {}
        for knob in station_config['knobs']:
            # Pull the knob config from the config and initialize the current 
            # value to zero.
            knob_config = station_config['knobs'][knob]
            knob_config['current_value'] = 0
            knob_config['last_update']   = 0
            knob_config['hint']          = None
            # Initialize randomized_sounds with the original list. It will be
            # shuffled later by an event after logging is configured.
            if 'sounds' in knob_config:
                knob_config['randomized_sounds'] = list(knob_config['sounds'])
            self.knobs[int(knob)]        = knob_config


    def randomize_sounds(self):
        """Randomize the sound mappings for each knob to create the puzzle."""
        logging.info("Randomizing puzzle sounds for station %d...", self.id)
        for id, knob in self.knobs.items():
            if 'sounds' in knob:
                shuffled_sounds = list(knob['sounds'])
                random.shuffle(shuffled_sounds)
                knob['randomized_sounds'] = shuffled_sounds
                
                # Find the new target position where the 'stationzap' sound is located
                for i, sound in enumerate(shuffled_sounds):
                    logging.info("Knob %d position %d assigned sound: %s", id, i, sound)
                    if sound.startswith("stationzap"):
                        knob['target_position'] = i
                
                logging.info("Knob %d target position is now %d ('%s')", id, knob['target_position'], shuffled_sounds[knob['target_position']])

    ##
    # Update the station's values.
    def update(self, analog_inputs):
        new_events = []
        for id in self.knobs:
            knob = self.knobs[id]

            # The analog inputs array is zero-indexed, the knob numbers are
            # indexed starting at 1.
            new_position = self._analog_value_to_position(analog_inputs[id - 1])
   
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

            # Generate the hints, if we've matched.
            if new_position == knob['target_position']:
                # if Config.get('visual-hint'):
                #     # Start the hint flasher.
                #     event = pixel_flash.Event(
                #                     when      = time.time(),
                #                     pixel_ids = [ self.get_pixel(id) ], 
                #                     color     = Color("#ffffff"),
                #                     period    = VISUAL_HINT_TIME,
                #                     ratio     = 0.1)
                #     knob['hint'] = event
                #     new_events.append(event)

                if Config.get('audio-hint'):
                    # Play the hint sound.
                    event = play_sound.Event(
                                    when       = time.time(), 
                                    station_id = self.id, 
                                    sound      = self.get_sound_hint(id))
                    new_events.append(event)

            # No match, no hint, just update the pixel color.
            else:
                # If we've got the hint flasher running, stop it.
                if knob['hint']:
                    # knob['hint'].stop_hint()
                    knob['hint'] = None
                
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
        # If we haven't heard from this station in the timeout interval,
        # then we assume it's dead and say that the condition's been met.
        if (time.time() - self.last_update_time) > STATION_TIMEOUT:
            return True

        # Iterate across all of the knobs, and if any of them don't match,
        # then we haven't met the condition.
        for id in self.knobs:
            knob = self.knobs[id]

            # If we haven't been updated since the last main event, then we 
            # havent met the criteria.
            if knob['last_update'] < SystemState.get_state_entry_time():
                return False

            # If the current value doesn't match the target position, then
            # we haven't met the criteria.
            if knob['current_value'] != knob['target_position']:
                return False

        # Everyone matches, this station is all set.
        return True

    #
    # Translate an analog input value to a knob position.
    def _analog_value_to_position(self, analog_value):
        # Handle digital IO Pi board input (values 1-8 from control-scan)
        # The IO Pi reads which pin is HIGH on the multiplexer, returning 1-8
        if 1 <= analog_value <= KNOB_POSITION_COUNT:
            # Convert pin number (1-8) to position index (0-7)
            return int(analog_value) - 1

        # Handle original analog ADC input (voltage 0-5V)
        # This preserves backward compatibility with the original hardware
        position = int((analog_value / MAX_KNOB_VOLTAGE) * KNOB_POSITION_COUNT)
        position = max(position, 0)
        position = min(position, KNOB_POSITION_COUNT - 1)
        return position
