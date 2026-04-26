#!/usr/bin/python3

import ads1256

ads1256.initialize()
ads1256.configure(ads1256.ADS1256_GAIN_1, ads1256.ADS1256_100SPS)

print("ADS1256 Chip ID: ", ads1256.get_chip_id())
print("")

results = ads1256.read_channels(0, ads1256.ADS1256_SINGLE_CHANNEL_COUNT - 1, ads1256.ADS1256_INPUT_SINGLE_ENDED)

for channel, value in enumerate(results):
    print("Channel", channel, ":", "{0:.3f}".format(value), "volts")

ads1256.shutdown()
