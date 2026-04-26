# update_queue.py - A queue to handle station updates.

import logging

# This class implements a thread which takes station updates from the web 
# service thread and updates the master state.

from threading import Condition, Thread
from queue import Queue

from master.state_tracker import StateTracker

class UpdateWorker(Thread):
    ##
    # Initialize the queue.
    #
    def __init__(self):
        # Initialize the thread and set it to be a 'daemon', so that we won't
        # keep the process from exiting if the main thread dies.
        Thread.__init__(self)
        self.daemon = True

        # Synchronization object between producer and consumer methods
        self.condition = Condition()

        # Priority queue keeps work items sorted in order of appearance
        self.queue = Queue()

        # Largest handled work item sequence number - keeps requests ordered
        self.sequence_number = 0

    ##
    # Thread body.
    #
    def run(self):
        # Run in a loop, picking up work items as they arrive and handling them
        while True:
            # Acquire the lock condition.
            self.condition.acquire()

            # Wait until the queue's got something in it.
            while self.queue.empty():
                self.condition.wait()

            # Pull the next update off the queue.
            station_update = self.queue.get()

            # Release the lock condition.
            self.condition.release()

            logging.debug("Dequeued station update: %s", station_update)

            # Now pass the work item to the callbacks.
            try:
                StateTracker.update_state(station_update)

            except Exception as e:
                logging.exception("Error dispatching station update")

    ##
    # Standard method for queueing up a work item to the pool
    #
    def queue_station_update(self, station_update):
        self.condition.acquire()

        self.queue.put(station_update)

        self.condition.notify()
        self.condition.release()

        logging.debug("Queued station update: %s", station_update)
        logging.debug("Queue size now: %d",        self.queue.qsize())


