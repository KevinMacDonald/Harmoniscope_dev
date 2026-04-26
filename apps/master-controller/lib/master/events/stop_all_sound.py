# events/stop_all_sound.py - An event to stop all sounds on a station.

import requests

from master.config import Config
from master.events import event

class Event(event.Event):
    ##
    # Initialize a station all-quiet event.
    #
    # @param when       - The time at which to update the pixel.
    # @param station_id - The station ID to send the event to.
    #
    def __init__(self, when, station_id):
        self.when       = when
        self.station_id = station_id

        if Config.get("sound-server"):
            self.sound_server = Config.get("sound-server")
        else:
            self.sound_server = "station" + str(self.station_id)

        self.base_url = "http://" + self.sound_server + ":9000/silent"

    def type(self):
        return "stop_all_sound"

    def run(self):
        try:
            response = requests.get(self.base_url)

        except requests.exceptions.RequestException as error:
            print("Error sending all sound stop to station:", error) 
        
