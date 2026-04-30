# events/play_sound.py - An event to play a sound on a station.

import logging
import time
import requests

from master.config import Config
from master.events import event

class Event(event.Event):
    ##
    # Initialize a sound playing event.
    #
    # @param when       - The time at which to update the pixel.
    # @param station_id - The ID of the station on which to play the sound,
    #                     or the station's hostname.
    # @param sound      - The name of the sound to play.
    # @param device     - The sound device on the station to play the
    #                     sound through (optional).
    #
    def __init__(self, when, station_id, sound, device = None):
        self.when       = when
        self.station_id = station_id
        self.sound      = sound
        self.device     = device

        if Config.get("sound-server"):
            self.sound_server = Config.get("sound-server")
        else:
            # If it's an integer, it's a station ID. 
            try:
                self.sound_server = "station" + str(int(self.station_id))

            # If not, it's a hostname.
            except ValueError:
                self.sound_server = str(self.station_id)

        self.base_url = "http://" + self.sound_server + ":9000/sound/"
        
    def type(self):
        return "play_sound"

    def run(self):
        url = self.base_url + str(self.sound)

        params = { }
        if self.device:
            params["device"] = self.device

        try:
            logging.info("Sending sound request to %s at %.2f", url, time.time())
            response = requests.get(url, params = params, timeout = 1)
            logging.info("Sound request returned status %s at %.2f", response.status_code, time.time())

        except requests.exceptions.RequestException as error:
            # Log the error cleanly without dumping the full Python stack trace
            logging.error("Error sending sound event to station: %s", error)
        
