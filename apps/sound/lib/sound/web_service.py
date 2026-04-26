# web_service.py - The sound server web service.

# Implements a RESTful web service using the Flask framework, running in an
# independent thread. Passes light state changes to a Worker thread using
# WorkItem instances in a queue.

import logging
import sys
import os.path

from flask import Flask, request
from threading import Thread

from sound.constants    import *
from sound.sound_player import SoundPlayer

class WebService:
    ##
    # Initialize the service and create the Flask server instance. Pass in the
    # sound player instance that will be used.
    #
    def __init__(self, options, sound_player):
        # Create the Flask app, and set up the request routing.
        self.app = Flask(__name__)

        self.app.add_url_rule('/sound/<sound_name>', 
                              'play_sound', self.play_sound)
        self.app.add_url_rule('/midi_on/<note>',  
                              'midi_on', self.midi_on)
        self.app.add_url_rule('/midi_off/<note>', 
                              'midi_off', self.midi_off)
        self.app.add_url_rule('/silent',          
                              'silent', self.silent)

        # Stash the sound player instance.
        self.sound_player = sound_player

    ##
    # Start the web service. Returns when the service exits (so, never).
    #
    def start(self):
        logging.debug("Starting Flask")
        # Start the Flask instance.
        self.app.run(debug        = False, 
                     host         = '0.0.0.0', 
                     port         = 9000, 
                     use_reloader = False, 
                     threaded     = False,
                     use_debugger = False)

    ##
    # Helper functions to sanitize input values.
    #
    def sanitize_note_value(self, note):
        note = int(note)
        if (note > MIDI_NOTE_MAX):
           return MIDI_NOTE_MAX
        if (note < MIDI_NOTE_MIN):
           return MIDI_NOTE_MIN
        return note

    def sanitize_instrument_value(self, instrument):
        instrument = int(instrument)
        if (instrument > INSTRUMENT_NUMBER_MAX):
            return INSTRUMENT_NUMBER_MAX
        if (instrument < INSTRUMENT_NUMBER_MIN):
            return INSTRUMENT_NUMBER_MIN
        return instrument

    def sanitize_velocity_value(self, velocity):
        velocity = int(velocity)
        if (velocity > MIDI_VELOCITY_MAX):
            return MIDI_VELOCITY_MAX
        if (velocity < MIDI_VELOCITY_MIN):
            return MIDI_VELOCITY_MIN
        return velocity

    ##
    # REST API handler for playing recorded sounds
    # This function will receive the instructions to play a particular sound
    #
    # @param <sound_name> - the name of the sound file to play
    # @param <device>     - the name of the device to play the sound on (optional)
    #
    # Restful API call example:
    #     http://192.168.8.116:7000/sound/blip
    #     http://192.168.8.116:7000/sound/blip?device=plughw:CARD=DAC
    #
    def play_sound(self, sound_name):
        try:
            device = request.args.get('device')
            if device is None:
                device = "default"

            self.sound_player.play_sound(sound_name, device)
            output = "Playing sound {}:".format(sound_name)
            logging.info(output)
        except Exception as error:
            output = "Error playing sound {}: {}".format(sound_name, error)
            logging.error(output)

        return output

    ############################################################################
    # REST API handler for playing MIDI notes
    # This function will play a MIDI note
    #
    # @param <Note> - note to play
    # @param <i> - instrument to use (defaults to 0)
    # @param <v> - velocity to use (defaults to 127)
    #
    # Restful API call examples:
    #    http://192.168.8.116:7000/midi_on/15?v=120&i=3 (note 15, velocity 120, instrument 3)
    #    http://192.168.8.116:7000/midi_on/50 (note 50, velocity 127, instrument 0)
    #
    def midi_on(self, note):
        note = self.sanitize_note_value(note)
        instrument = request.args.get('i', 0, type=int)
        instrument = self.sanitize_instrument_value(instrument)

        velocity = request.args.get('v', 127, type=int)
        velocity = self.sanitize_velocity_value(velocity)

        try:
            self.sound_player.note_on(note, instrument, velocity)
            output = "Playing note {}: velocity={}, instrument={}".format(note, velocity, instrument)
            logging.info(output)
        except Exception as error:
            output = "Error playing note {} (v={}, i={}):".format(note, velocity, instrument, error)
            logging.exception(output)

        return output

    ############################################################################
    # REST API handler for turning off MIDI notes
    # This function will stop a MIDI note
    #
    # @param <Note> - note to stop playing
    # @param <i> - instrument to use (defaults to 0)
    #
    # Restful API call examples:
    #    http://192.168.8.116:7000/midi_off/50 (note 50)
    #
    def midi_off(self, note):
        note = self.sanitize_note_value(note)

        instrument = request.args.get('i', 0, type=int)
        instrument = self.sanitize_instrument_value(instrument)

        try:
            self.sound_player.note_off(note, instrument)
            output = "No longer playing note {}".format(note)
            logging.info(output)
        except Exception as error:
            output = "Error stopping note {}: {}".format(note, error)
            logging.exception(output)

        return output

    ############################################################################
    # REST API handler for stopping sound
    # This function will stop all playback
    #
    # Restful API call example:
    #    http://192.168.8.116:7000/silent
    #
    def silent(self):
        try:
            self.sound_player.all_silent()
            output = "All sounds stopped"
            logging.info(output)
        except Exception as error:
            output = "Error stopping sound: {}".format(error)
            logging.exception(output)

        return output

