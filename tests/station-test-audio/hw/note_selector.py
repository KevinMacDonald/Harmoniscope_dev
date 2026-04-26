# Class to manage selecting the notes to play for a given knob.
#
# Create an instance of this class for each knob you have. When you create it,
# you specify the analog input line to use to control whether the note is on
# or off (the 'enable' line), and the input line you use to select which note
# to play (the 'selection' line).
#
# You also specify a "base note" for the selector instance, which is the lowest
# note value to select (when the knob is all the way down). The instance will
# then select notes starting at that base note and going up, depending on the
# voltage of the selection line.
#
# Once you've got an instance, you can then read in the analog values using the
# AnalogInput class, and pass the array of input analog values to the 
# update_selected_note() method to have it select the appropriate note.

class NoteSelector:
    # How many notes should there be in the range of selection input values.
    # Right now it's hard-coded to a full octave (12 notes).
    NUMBER_OF_NOTES = 12

    # Construct a NoteSelector instance. You need to pass in the line numbers
    # for enable and selection, the base note, and a MIDIControl instance to
    # allow the instance to start and stop MIDI notes playing.
    def __init__(self, enable_line, selection_line, base_note, midi_control):
        # Copy the parameters to the instance.
        self.enable_line     = enable_line
        self.selection_line  = selection_line            
        self.base_note       = base_note
        self.midi_control    = midi_control

        # Reset our state-tracking variables. 'cur_note' is the current note
        # being played, and 'enabled' indicates whether we're enabled or not.
        self.cur_note = base_note
        self.enabled  = False

    # Get the number of the currently selected note.
    def get_selected_note(self):
        return self.cur_note

    # Returns True if this note is enabled.
    def is_enabled(self):
        return self.enabled

    # Update the selected note based on the list of analog input values.
    #
    # Starts or stops the note playing over MIDI as appropriate.
    def update_selected_note(self, analog_values):
        # Get the voltage of the selection input.
        selection_voltage = analog_values[self.selection_line]

        # If it's a negative voltage, bump it up to zero. This can happen
        # if there's noise in the analog conversion.
        if selection_voltage < 0:
            selection_voltage = 0

        # Calculate the new note value by converting the voltage into an
        # offset note count, and adding it to the base note value.
        note_offset = int(round(selection_voltage / (5.0 / self.NUMBER_OF_NOTES)))
        new_note    = self.base_note + note_offset

        # Determine if the enable line is closer to 0 or +5 volts, to see if
        # this note should be enabled or not..
        enabled_value = analog_values[self.enable_line]
        enabled_new = False
        if enabled_value < 2.5:
            enabled_new = False
        else:
            enabled_new = True

        # If we're currently enabled and going to disabled, or changing notes,
        # stop the current note.
        if (self.enabled == True) and ((enabled_new == False) or (new_note != self.cur_note)):
            print("Stopping note:", self.cur_note)
            self.midi_control.stop_note(self.cur_note)

        # If we're going to be enabled and we're current not enabled, or 
        # we're switching notes, start the new note.
        if (enabled_new == True) and ((self.enabled == False) or (new_note != self.cur_note)):
            print("Starting note:", new_note)
            self.midi_control.start_note(new_note)

        # Copy the new state into our state tracking variables.
        self.enabled = enabled_new
        self.cur_note = new_note


