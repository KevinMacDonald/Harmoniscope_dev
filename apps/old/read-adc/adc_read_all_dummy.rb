#!/usr/bin/env ruby
#
# Mock ADC read utility. Always returns static values.
#

if ARGV.length == 1 && ARGV[0].equal?("-r")
  puts "0,1000,2000,3000"
else
  puts "Channel 0 Voltage Reading 0.010 (V) "
  puts "Channel 1 Voltage Reading 2.308 (V) "
  puts "Channel 2 Voltage Reading 1.809 (V) "
  puts "Channel 3 Voltage Reading 4.999 (V) "
end
