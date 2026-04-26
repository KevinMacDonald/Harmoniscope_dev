# events/stop_note.py - An event to stop a MIDI note on a station.

import requests

from master.config import Config
from master.events import event

class Event(event.Event):
    ##
    # Initialize a MIDI note stop event.
    #
    # @param when       - The time at which to update the pixel.
    # @param station_id - The station to play the note on.
    # @param note       - The MIDI note number to play.
    #
    def __init__(self, when, station_id, note):
        self.when       = when
        self.station_id = station_id
        self.note       = note

        if Config.get("sound-server"):
            self.sound_server = Config.get("sound-server")
        else:
            self.sound_server = "station" + str(self.station_id)

        self.base_url = "http://" + self.sound_server + ":9000/midi_off/"

    def type(self):
        return "stop_note"

    def run(self):
        url = self.base_url + str(self.note)

        try:
            response = requests.get(url)

        except requests.exceptions.RequestException as error:
            print("Error sending MIDI note to station:", error) 
        
