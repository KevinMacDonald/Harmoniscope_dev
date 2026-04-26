# analog_inputs.rb - A class for reading the values of the analog lines
#
# $Id: $

# AnalogInputs provides a set of methods for reading the voltages on the 
# analog input lines connected to the ADC. 
#
# There are four analog lines connected to the ADC, each connected to the
# center tap on a 10kOhm potentiometer wired between ground and Vcc (+5V).
#
# The ADC is connected to the Raspberry Pi via I2C. This class depends on 
# a utility program to read the values. That program returns a comma-separated
# list of values between -32,768 and +32,767, representing voltages between
# -6.144 and +6.144 volts.
#
# The program returns the values for all 4 input lines at once. Those values
# are cached, and will be returned until the values are re-read by calling
# read_values().
#
# == Example
#
#   require 'analog_inputs'
#
#   analog_inputs = AnalogInputs.new
#
#   voltage = analog_inputs.get_value(1)
#   puts "Analog line 1 is at #{voltage*6.144/32767} volts."
#
#   sleep 1
#
#   analog_inputs.read_values
#   voltage = analog_inputs.get_value(1)
#   puts "Analog line 1 is now at #{voltage*6.144/32767} volts."

class AnalogInputs
  # The location of the ADC helper tool.
  @@ADC_INPUT_PROGRAM = "/home/pi/harmoniscope/a2d-test/read_all -r"

  # The most recent set of values read from the ADC
  @cur_values

  # Initialize a new instance. Currently does nothing.
  def initialize()
  end
 
  # Read the current voltage values from the ADC. 
  def read_values()
    output = `#{@@ADC_INPUT_PROGRAM}`
    raise "Error reading ADC values (#{$?.exitstatus})" if ($?.exitstatus != 0)

    @cur_values = output.split(',').map(&:to_i)

    unless @cur_values.length == 4
      raise "Incorrect number of analog inputs (#{@cur_values.length})" 
    end
  end

  # Get the voltage value that was read in for the given line_number.
  def get_value(line_number)
    line_number = line_number.to_i

    unless line_number >= 0 && line_number < 4
      raise "Invalid analog line number #{line_number}" 
    end

    return @cur_values[line_number]
  end
end

