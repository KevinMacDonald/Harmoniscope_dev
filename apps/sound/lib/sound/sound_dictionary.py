# sound_dictionary.py - dictionary of all the sounds recognized by this code

import re
import os.path

class SoundDictionary:
    ##
    # Initialize the dictionary of sound file names.
    #
    def __init__(self, options):
        self.sound_directory = options["sound-directory"]

        # Allow sound names to contain alphanumerics, plus dash, underscore 
        # and period.
        self.name_pattern = re.compile('^[-\w_.]+$')

    ##
    # Look up the file name for the given sound.
    #
    def get_file_name(self, sound_name):
        if not self.name_pattern.match(sound_name):
           raise ValueError("Invalid sound name")

        sound_path = self._full_path(sound_name)
        if not os.path.isfile(sound_path):
           raise ValueError("Sound file not found")

        return sound_path

    ##
    # Generate a filepath for the given sound file.
    #
    def _full_path(self, file_name):
        return self.sound_directory + file_name + ".wav"

