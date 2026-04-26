# midi_control.rb - A class for controlling MIDI output
#
# $Id: $

require "unimidi"

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
# == Example
#
#   require 'midi_control'
#
#   midi = MIDIControl.new
#
#   midi.start_note(36)
#   sleep 1
#   midi.stop_note(36)

class MIDIControl
  # The default channel to use
  @@DEFAULT_CHANNEL = 15

  # The channel specifies which MIDI voice to use.
  @channel

  # The UniMIDI output device.
  @output

  # A Hash to track the counts of which notes are playing.
  @note_counts

  # Create a new MIDI control instance. Specify the channel (synthesizer voice)
  # you wish to use. 
  def initialize(channel = @@DEFAULT_CHANNEL)
    @output      = UniMIDI::Output.use(:first)
    @channel     = channel
    @note_counts = {}
  end

  # Start playing the given note, or increment its counter if it's already
  # playing.
  #
  # Set force to true to force a new start note message to be sent. This
  # will usually cause a new key press to occur. The note counter will
  # still be incremented.
  def start_note(note, force = false)
    if (!@note_counts.has_key?(note) || @note_counts[note] == 0)
      @output.puts(0x90 + @@CHANNEL, note, 100) # note on
      @note_counts[note] = 1
    else
      @output.puts(0x90 + @@CHANNEL, note, 100) if force == true
      @note_counts[note] += 1
    end
  end

  # Decrement the given note's counter, and stop playing it if its counter
  # reaches zero.
  #
  # Set force to true to force the note to stop and reset its counter to zero.
  def stop_note(note, force = false)
    if (!@note_counts.has_key?(note) || @note_counts[note] == 0)
      return
    end

    if (force == true)
      @note_counts[note] = 0 
      @output.puts(0x80 + @@CHANNEL, note, 100) # note off
      return
    end

    @note_counts[note] -= 1
    if (@note_counts[note] == 0)
      @output.puts(0x80 + @@CHANNEL, note, 100) # note off
    end
  end
end
