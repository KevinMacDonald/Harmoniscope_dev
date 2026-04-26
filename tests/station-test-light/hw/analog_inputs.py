# analog_inputs.py - A class for reading the values of the analog lines
#
# AnalogInputs provides a set of methods for reading the voltages on the 
# analog input lines connected to the ADC. 
#
# There are 8 analog lines connected to the ADC. The first four (lines 0-3)
# are connected to the center tap on a 10kOhm potentiometer wired between 
# ground and Vcc (+5V). They will read values between 0 and 5V, depending on
# the position of the knob. The second four (lines 4-7) are used as jumpers,
# and will read either around 0 volts, or around 5 volts (things aren't 
# exact here).
#
# This class is a simple wrapper around the ads1256-py library, so see that
# for details on how to use the ADC.
#
# Depends on the ads1256 Python module and the supporting C library.

import ads1256

class AnalogInputs:
    # A state variable to ensure that we only initialize the ADS1256 once.
    initialized = False

    # Constructor for an instance of the class. Takes no parameters.
    def __init__(self):
        # If the ADS1256 hasn't been initialized yet, initialize it and
        # configure it.
        if AnalogInputs.initialized == False:
            ads1256.initialize()

            # We configure it with a gain of 1 (no gain), and to sample at
            # 1000 samples per second (SPS).
            ads1256.configure(ads1256.ADS1256_GAIN_1, ads1256.ADS1256_1000SPS)

            # Set the flag to indicate that we've been initialized.
            AnalogInputs.initialized = True

    # Read the current voltage values from the ADC. 
    #
    # Returns a list of 8 values.
    def read_values(self):
        # We're doing single-ended (not differential) analog conversions,
        # and we want to read channels from 0 to the maximum.
        return ads1256.read_channels(0, 
                                     ads1256.ADS1256_SINGLE_CHANNEL_COUNT - 1, 
                                     ads1256.ADS1256_INPUT_SINGLE_ENDED)

