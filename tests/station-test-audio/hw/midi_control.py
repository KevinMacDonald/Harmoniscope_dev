# midi_control.py - A module for controlling MIDI output

# MIDIControl provides a set of methods for controlling the MIDI output to
# the software synthesizer.
#
# The software synthesizer is polyphonic (it can play multiple notes 
# simultaneously), and takes in numeric MIDI values (36 is note C1, for 
# example). You control it by sending start and stop signals for specific
# note values.
#
# This class provides an abstraction for the note playing interface that helps
# when you have multiple sources generating the same possible notes. Repeated
# calls to start a note are counted, and must be matched by an equal number
# of stop notes before the note is actually stopped from playing. 
#
# Depends on rtmidi: https://pypi.python.org/pypi/python-rtmidi 

import rtmidi

class MIDIControl:
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


    # Create a new MIDI control instance. Specify the channel (synthesizer
    # voice) you wish to use. 
    def __init__(self, channel = DEFAULT_CHANNEL):
        # Set the requested channel.
        self.channel = channel

        # Reset the note counts to an empty Dictionary.
        self.note_counts = {}

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
            raise Exception("No matching port found, aborting.")


    # A destructor to cleanup when we're shut down. The main thing we want
    # to do is stop all notes, so that we don't leave anything stuck on.
    def __del__(self):
        self.stop_all_notes()
        del self.midiout

   
    # Start playing the given note, or increment its counter if it's already
    # playing.
    #
    # Set force to true to force a new start note message to be sent. This
    # will usually cause a new key press to occur. The note counter will
    # still be incremented. 
    def start_note(self, note, force = False):
        # If we aren't tracking this note, or if our counts show that the
        # note isn't currently playing, then start the note playing.
        if note not in self.note_counts or self.note_counts[note] == 0:
            self.send_note_on(note)
            self.note_counts[note] = 1

        # Otherwise, just increment the note count (unless 'force' is True,
        # in which case we send a start note command.
        else:
            if force == True:
                self.send_note_on(note)
            self.note_counts[note] += 1


    # Decrement the given note's counter, and stop playing it if its counter
    # reaches zero.
    #
    # Set force to true to force the note to stop and reset its counter to zero.
    def stop_note(self, note, force = False):
        # If we're told to force an action, then stop the note, reset the
        # count, and return.
        if force == True:
            self.send_note_off(note)
            self.note_counts[note] = 0
            return

        # If we're not tracking this note, or if our counts show that the note
        # isn't playing, then don't do anything.
        if note not in self.note_counts or self.note_counts[note] == 0:
            return

        # Decrement the note count.
        self.note_counts[note] -= 1

        # If we're down to zero, send a stop note.
        if self.note_counts[note] == 0:
            self.send_note_off(note)


    # Stop all notes playing and reset the note counts to zero.
    def stop_all_notes(self):
        # 120 and 0 are control values specified in the MIDI spec. 
        self.midiout.send_message([self.MIDI_ALL_SOUND_OFF + self.channel, 
                                   120, 
                                   0])
        self.note_counts = {}


    # Helper function to send a 'note on' message. We hardcode a velocity
    # of 100 (maximum is 127)
    def send_note_on(self, note):
        self.midiout.send_message([self.MIDI_NOTE_ON + self.channel, 
                                   note, 
                                   100])


    # Helper function to send a 'note off' message. We hardcode a velocity
    # of 100 (maximum is 127)
    def send_note_off(self, note):
        self.midiout.send_message([self.MIDI_NOTE_OFF + self.channel, 
                                   note, 
                                   100])
    
