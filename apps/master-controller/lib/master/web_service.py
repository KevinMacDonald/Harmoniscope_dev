# web_service.py - The master controller web service.

# Implements a RESTful web service using the Flask framework. Passes station
# events to a Worker thread using a queue.

import logging
import time

from flask     import Flask, request
from threading import Thread

from master.constants      import *
from master.config         import Config 
from master.update_queue   import UpdateWorker
from master.event_queue    import EventWorker
from master.station_update import StationUpdate
from master.events         import load_event_script

class WebService(Thread):
    ##
    # Initialize the Flask server instance.
    #
    # @param <update_queue>  - The queue to place station updates on.
    #
    def __init__(self, update_queue):
        self.update_queue  = update_queue

        # Initialize the thread and set it to be a 'daemon', so that we won't
        # keep the process from exiting if the main thread dies.
        Thread.__init__(self)
        self.daemon = True

        # Create the Flask app, and set up request routing.
        self.app = Flask(__name__)
        self.app.add_url_rule('/station/<station_id>', 
                              'update_station', 
                              self.update_station)
        self.app.add_url_rule('/main_event',
                              'fire_main_event', 
                              self.fire_main_event)

    ##
    # Run the web server.
    #
    def run(self):
        self.app.run(debug        = False, 
                     host         = '0.0.0.0', 
                     port         = 7000, 
                     use_reloader = False, 
                     threaded     = False,
                     use_debugger = False)

    ##
    # This function will process the analog values from each station to 
    # calculate lighting effects, Then it will send the analog values back 
    # to each station for computation of sound.
    #
    # @param <station>       - the address of the station for which data 
    #                          is being processed
    # @param <analog_values> - a list of the analog values to process
    # @param <stop_victory>  - a boolean of whether an active victory sequence 
    #                          needs to be ended and reset
    #
    # @return Response/output to render to a browser
    #
    # Restful API call example: 
    #
    #   http://192.168.8.111:7000/station/1?analog_values=1,2,3,4
    #
    def update_station(self, station_id):
        # XXX: Validate station ID.

        # Get the list of analog input parameters
        analog_input = request.args.get('analog_values')
        if analog_input is None:
            output = "No analog inputs provided to master controller."
            print(output)
            return output

        analog_input = analog_input.replace('[', '').replace(']', '')
        analog_values = [float(f) for f in analog_input.split(',')]

        # XXX: Turn these into actual checks.
        assert isinstance(analog_values, list)
        assert len(analog_values) == 4

        station_update = StationUpdate(int(station_id), analog_values)
        self.update_queue.queue_station_update(station_update)
        
        output = "Input accepted for {} : {}".format(station_id, analog_values)
        logging.info(output)
        return output

    ##
    # This function will manually trigger the main event.
    #
    # @return Response/output to render to a browser
    #
    # Restful API call example: 
    #
    #   http://192.168.8.111:7000/main_event
    #
    def fire_main_event(self):
        event = load_event_script.Event(
                                when        = time.time(), 
                                script_file = MAIN_EVENT_SCRIPT)
        EventWorker.replace_queue([event])

        output = "Main event manually triggered!"
        logging.info(output)
        return output


