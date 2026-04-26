#!/usr/bin/env ruby

$LOAD_PATH.unshift(File.dirname(__FILE__) + "/../../lib/ruby")
puts $LOAD_PATH

require "hw/analog_inputs"
require "hw/digital_inputs"
require "hw/midi_control"

# 
# MAIN CODE
#

$REFRESH_INTERVAL = 0.01 # Seconds

midi           = MIDIControl.new
analog_inputs  = AnalogInputs.new

note_selectors = [
  NoteSelector.new(18, 0, 36),  # Base note of C1
  NoteSelector.new(19, 1, 36),  # Base note of E1
  NoteSelector.new(20, 2, 36),  # Base note of G1
  NoteSelector.new(21, 3, 36),  # Base note of C2
]

begin
  loop do
    analog_inputs.read_values()

    note_selectors.each do |x|
      cur_note = x.get_selected_note() 

      if (DigitalInputs.pin_set?(x.enable_pin) == true) 
        if (!x.enabled?)
          puts "Enabling pin #{x.enable_pin}"
          x.set_enabled(true)
          midi.start_note(cur_note)
        end
      else
        if (x.enabled?)
          puts "Disabling pin #{x.enable_pin}"
          x.set_enabled(false)
          midi.stop_note(cur_note)
        end
        next
      end

      new_note = x.update_selected_note(analog_inputs)

      if (cur_note != new_note) 
        midi.stop_note(cur_note);
        midi.start_note(new_note);
      end
    end

    sleep($REFRESH_INTERVAL)
  end

rescue SystemExit, Interrupt
  note_selectors.each do |x|
    midi.stop_note(x.get_selected_note())
  end  
end
