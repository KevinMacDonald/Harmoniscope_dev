# station_update.py - implementation of the station update tracking class

# StationUpdate provides a unit of state change for a station.
# It contains a station ID and a set of knob values for that station.
# The update is queued up to the worker thread where it is handled.

class StationUpdate:
    def __init__(self, station_id, analog_values):
        # Make sure the station ID is sane.
        self.station_id = int(station_id)
        assert(self.station_id >= 0)

        # Copy the station update details over.
        self.analog_values = analog_values

