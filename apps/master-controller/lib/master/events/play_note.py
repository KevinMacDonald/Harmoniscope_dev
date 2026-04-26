# events/play_note.py - An event to play a MIDI note on a station.

import requests

from master.config import Config
from master.events import event

class Event(event.Event):
    ##
    # Initialize a MIDI note playing event.
    #
    # @param when       - The time at which to update the pixel.
    # @param station_id - The station ID to send the event to.
    # @param note       - The MIDI note number to play.
    # @param instrument - The MIDI instrument to use.
    # @param velocity   - The note velocity.
    #
    def __init__(self, when, station_id, note, instrument, velocity):
        self.when       = when
        self.station_id = station_id
        self.note       = note
        self.instrument = instrument
        self.velocity   = velocity

        if Config.get("sound-server"):
            self.sound_server = Config.get("sound-server")
        else:
            self.sound_server = "station" + str(self.station_id)

        self.base_url = "http://" + self.sound_server + ":9000/midi_on/"

    def type(self):
        return "play_note"

    def run(self):
        url = self.base_url + str(self.note)

        params = {
            "v": self.velocity,
            "i": self.instrument
            }

        try:
            response = requests.get(url, params = params)

        except requests.exceptions.RequestException as error:
            print("Error sending MIDI note to station:", error) 
        
