#!/usr/bin/python3
#
# Simple program to demonstrate reading inputs from the hardware and generating
# sound using MIDI notes sent to the software synthesizer.
#
# Run as root:
#
#    sudo ./station_test.py
#
# See the README.txt file for more information.

# Import standard libraries.
import time

# Import our custom libraries from the 'hw' subdirectory.
from hw.analog_inputs import AnalogInputs
from hw.note_selector import NoteSelector
from hw.midi_control  import MIDIControl

# Create an instance of the AnalogInputs class to read in the analog values
# from the knobs and switches.
analog_in     = AnalogInputs()

# Create an instance of the MIDIControl class that generates MIDI notes and
# tracks which ones are playing.
midi_control  = MIDIControl()

# Instantiate a set of NoteSelector classes. 
#
# We specify the following parameters for each one:
# - Jumper input line: if this has a high voltage, the note selector is enabled.
# - Input knob line: The voltage here determines the note selected.
# - Base note: What note to start the selection range at.
# - MIDI control: The MIDIControl object to use to start and stop notes.
note_selectors = [
    NoteSelector(4, 0, 60, midi_control), # Base note of middle C
    NoteSelector(5, 1, 60, midi_control), # Base note of middle C
    NoteSelector(6, 2, 60, midi_control), # Base note of middle C
    NoteSelector(7, 3, 60, midi_control), # Base note of middle C
    ]

# Now we loop forever.
while True:
    # Read in the current values of all of the analog lines.    
    inputs = analog_in.read_values()

    # Iterate across each note selector and tell it to update itself based
    # on the analog line values.
    for note in note_selectors:
        note.update_selected_note(inputs)
	
