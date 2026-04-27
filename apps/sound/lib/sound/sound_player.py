# sound_player.py - Encapsulates the audio control functionality.

import logging
import rtmidi
import simpleaudio as sa

from threading import Lock

from sound.constants import *
from sound.sound_dictionary import SoundDictionary

class SoundPlayer:
    # The 'channel' on the synthesizer that we want to use. The synth has
    # 16 voices, and specifying channels above 16 uses the same voices with
    # different effects.
    DEFAULT_CHANNEL = 15 


    # Base values for different MIDI commands. For each of these, add in 
    # the channel number (0 through 15) to specify the channel you wish to
    # affect.
    #
    # This page lists the different MIDI messages:
    #
    #  https://www.midi.org/specifications/item/table-1-summary-of-midi-message
    #
    MIDI_NOTE_ON       = 0x90
    MIDI_NOTE_OFF      = 0x80
    MIDI_ALL_SOUND_OFF = 0xB0

    # Initialize and create the sound player. Sets up pygame to play sound.
    def __init__(self, config):
        self.sound_dictionary = SoundDictionary(config)
        self.channel = 1

        try:
            self.initialize_wav_player()
            self.initialize_midi_player()

        except:
            logging.exception("Failure initializing audio")
            raise

        # Configure the set to track which notes are playing.
        self.note_set      = dict()
        self.note_set_lock = Lock()

        self.initialized = True

    def initialize_wav_player(self):
        logging.debug("Initializing audio output")

    def initialize_midi_player(self):
        # Create a new MIDI output object.
        self.midiout = rtmidi.MidiOut()

        # There are a number of different MIDI "ports" on the Linux system,
        # each representing a device. We want to use the virtual port for
        # the FluidSynth process, so we enumerate across them until we find
        # one whose name contains "FLUID".
        available_ports = self.midiout.get_ports()

        port_number = None
        for number, port in enumerate(available_ports):
            if "FLUID" in port:
                # We've found the right one, use it.
                port_number = number
                break

        # If we found the FluidSynth port, use it. Otherwise, complain and
        # throw an exception.
        if port_number:
                self.midiout.open_port(port_number)
        else:
            logging.warning("No FluidSynth MIDI port found. MIDI functions will be disabled.")
            self.midiout = None

    # A destructor to cleanup when we're shut down. The main thing we want
    # to do is stop all notes, so that we don't leave anything stuck on.
    def __del__(self):
        if not hasattr(self, 'initialized'):
            return

        self.all_silent(stop_midi=False)
        del self.midiout

    # Play the sound with the given file name.
    def play_sound(self, sound_name, device):
        file_name = self.sound_dictionary.get_file_name(sound_name)
        wave_obj = sa.WaveObject.from_wave_file(file_name)
        play_obj = wave_obj.play()
 
    # Play the given MIDI note on the instrument with the chosen velocity.
    def note_on(self, note, instrument, velocity):
        with self.note_set_lock:
            if instrument in self.note_set and note in self.note_set[instrument]:
                # If the note is already playing, we have to turn it off
                # before we start playing a new note.
                logging.info("Note {} already playing, stopping".format(note))
                self._send_note_off(note, instrument)

            # Add the note to the set so that we remember that it's playing.
            if instrument not in self.note_set:
                self.note_set[instrument] = set()
            self.note_set[instrument].add(note) 
           
            # Now play the note. 
            self._send_note_on(note, instrument, velocity)
 
    # Stop playing the given MIDI note.
    def note_off(self, note, instrument):
        with self.note_set_lock:
            if instrument in self.note_set and note in self.note_set[instrument]:
                logging.info("Stopping note {}".format(note))

                # Remove the note from the set of notes currently playing.
                self.note_set[instrument].remove(note) 

                # Stop the note.
                self._send_note_off(note, instrument)

            else:
                logging.info("Note {} not playing, ignoring off command".format(note))
 
    # Stop all sounds.
    def all_silent(self, stop_midi=True):
        # Stop all currently playing sounds.
        sa.stop_all()

        # Only attempt to send MIDI commands if the MIDI port was successfully initialized.
        if self.midiout and stop_midi:
            with self.note_set_lock:
                for instrument in self.note_set:
                    # 120 and 0 are control values specified in the MIDI spec.
                    self.midiout.send_message([self.MIDI_ALL_SOUND_OFF + instrument,
                                               120,
                                               0])
                self.note_set.clear()

    # Helper function to send a 'note on' message. We hardcode a velocity
    # of 100 (maximum is 127)
    def _send_note_on(self, note, instrument, velocity):
        if not self.midiout: return
        logging.debug("Sending Note on %d, %d, %d" % (note, instrument, velocity))
        self.midiout.send_message([self.MIDI_NOTE_ON + instrument,
                                   note, 
                                   velocity])


    # Helper function to send a 'note off' message. We hardcode a velocity
    # of 127 (maximum is 127)
    def _send_note_off(self, note, instrument):
        if not self.midiout: return
        logging.debug("Sending Note off %d, %d" % (note, instrument))
        self.midiout.send_message([self.MIDI_NOTE_OFF + instrument, 
                                   note, 
                                   127])

    
