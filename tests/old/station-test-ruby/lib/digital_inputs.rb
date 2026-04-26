# digital_inputs.rb - A class to read the state of the digital inputs.
#
# $Id: $

# DigitalInputs provides a set of methods to read the state of the digital
# inputs connected to the Raspberry Pi's GPIO lines.
#
# There are four DIP switches wired up to the Pi, connected to pins 18 through
# 21. They are wired to ground, and the Pi's pull-up resistor should be set.
# This means that when the switch is "ON", the pin will be connected to ground,
# and will read 0. When the switch is "OFF", the pin will be held high by
# the pull-up resistor, and will read 1. This class corrects that inversion,
# using a 'true' value to indicate that the switch is set to "ON".
#
# == Example
#
#    require 'digital_inputs'
#
#    if DigitalInputs.pin_set?(18)
#      puts "I/O pin 18 is currently set"
#    end

class DigitalInputs
  # The format string used to generate the filepath for reading the GPIO pin
  # values.
  @@BASE_PATH = "/sys/class/gpio/gpio%d/value"

  # Returns true if the given GPIO pin is set. Pin numbering is 
  def self.pin_set?(pin)
    path = sprintf(@@BASE_PATH, pin.to_i)
    value = File.read(path)

    # The switches are wired up with inverse polarity and a pull-down. "ON"
    # results in a 0 value.
    return false if (value.start_with?("1"))

    true
  end
end
