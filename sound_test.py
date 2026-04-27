#!/usr/bin/python3
#
# Harmoniscope - Standalone Sound Test
#
# This script attempts to play a known WAV file using the simpleaudio library
# to verify that the audio hardware and library are functioning correctly.
#
import simpleaudio as sa
import sys

# This test file is included with the simpleaudio library source.
WAV_FILE_PATH = 'apps/sound/simpleaudio-1.0.1/simpleaudio/test_audio/c.wav'

print("--- Harmoniscope Sound Test ---")

try:
    print("Attempting to play: {}".format(WAV_FILE_PATH))
    wave_obj = sa.WaveObject.from_wave_file(WAV_FILE_PATH)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until the sound has finished playing
    print("Playback finished successfully.")
except Exception as e:
    print("An error occurred: {}".format(e), file=sys.stderr)