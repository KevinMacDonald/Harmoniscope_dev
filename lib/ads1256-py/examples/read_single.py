#!/usr/bin/python3

import sys
import ads1256

if (len(sys.argv) != 2):
    print("Usage: read_single.py <channel>")
    sys.exit(-1)

ads1256.initialize()
ads1256.configure(ads1256.ADS1256_GAIN_1, ads1256.ADS1256_100SPS)

channel = int(sys.argv[1])
value   = ads1256.read_channel(channel, ads1256.ADS1256_INPUT_SINGLE_ENDED)
print("Channel ", sys.argv[1], ": ", "{0:.3f}".format(value), "volts")

ads1256.shutdown()
