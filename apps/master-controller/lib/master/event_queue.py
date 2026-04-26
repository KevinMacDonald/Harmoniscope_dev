# event_queue.py - A queue to handle station events.

import logging
import random
import time

# This class implements a thread which takes events from the state tracker 
# executes them in a timely manner.

from threading import Condition, Thread
from queue import PriorityQueue

from master.config import Config

class EventWorker(Thread):
    # Synchronization object between producer and consumer methods
    condition = Condition()

    # Priority queue keeps work items sorted in order of appearance
    queue = PriorityQueue()

    ##
    # Initialize the queue. 
    #
    def __init__(self):
        # Initialize the thread and set it to be a 'daemon', so that we won't
        # keep the process from exiting if the main thread dies.
        Thread.__init__(self)
        self.daemon = True

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

            # Pull the work item off the queue.
            (event_time, event) = self.queue.get()

            # If it's not time for the event, put it back and wait until
            # it is.
            if (event_time > time.time()):
                self.queue.put([event_time, event])
                self.condition.release()
                continue

            # Release the lock condition.
            self.condition.release()

            logging.debug("Dequeued %s event at %.2f (delta: %.2f)", 
                          event.type(), time.time(), time.time() - event_time)
            logging.debug("Queue size now %d" % self.queue.qsize())

            # Now run the event.
            try:
                new_events = event.run()

                if new_events:
                    EventWorker.queue_events(new_events) 

            except Exception as error:
                logging.exception("Error dispatching event")

    ##
    # Standard method for queueing up a work item to the pool
    #
    def queue_event(event):
        EventWorker.condition.acquire()
        EventWorker.queue.put([event.when + (random.random() / 100000), event])

        logging.debug("Queued event to run at %.2f: %s", event.when, event.type())

        EventWorker.condition.notify()
        EventWorker.condition.release()

    ##
    # Standard method for queueing up a list of work items to the pool
    #
    def queue_events(events):
        EventWorker.condition.acquire()
        
        for event in events:
            EventWorker.queue.put([event.when + (random.random() / 100000), event])
            logging.debug("Queued event to run at %.2f: %s", event.when, event.type())

        EventWorker.condition.notify()
        EventWorker.condition.release()

    ##
    # Replace all events in the queue with the given events.
    #
    def replace_queue(events):
        EventWorker.condition.acquire()

        while not EventWorker.queue.empty():
            EventWorker.queue.get()

        for event in events:
            EventWorker.queue.put([event.when + (random.random() / 100000), event])
            logging.debug("Queued event to run at %d: %s", event.when, event.type())

        EventWorker.condition.notify()
        EventWorker.condition.release()

