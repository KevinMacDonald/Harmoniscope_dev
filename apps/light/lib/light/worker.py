# worker.py - implementation of the light server's main consumer thread

# This class implements a thread which takes work items from the web service
# thread and dispatches them to the UI simulator and DMX handler.

import logging

from threading import Condition, Thread
from queue import PriorityQueue

class Worker(Thread):
    # Initialize the worker. Pass in a list of "callbacks": objects that 
    # implement the update_pixels() method, which will get passed every
    # work item from the web service.
    def __init__(self, callbacks):
        # Initialize the thread and set it to be a 'daemon', so that we won't
        # keep the process from exiting if the main thread dies.
        Thread.__init__(self)
        self.daemon = True

        # Stash the callbacks list.
        self.callbacks = callbacks

        # Synchronization object between producer and consumer methods
        self.condition = Condition()

        # Priority queue keeps work items sorted in order of appearance
        self.queue = PriorityQueue()

        # Largest handled work item sequence number - keeps requests ordered
        self.sequence_number = 0

    # Thread body.
    def run(self):
        # Run in a loop, picking up work items as they arrive and handling them
        while True:
            # Acquire the lock condition.
            self.condition.acquire()

            # Wait until the queue's got something in it.
            while self.queue.empty():
                self.condition.wait()

            # Pull the work item off the queue.
            (sequence_number, work_item) = self.queue.get()

            # Make sure that the work item is coming in the correct order, 
            # and put it back on the queue if not..
            if sequence_number != self.sequence_number + 1:
                self.queue.put([sequence_number, work_item])
            else:
                self.sequence_number += 1

            # Release the lock condition.
            self.condition.release()

            logging.debug("Dequeued work item: %d", sequence_number)

            # Now pass the work item to the callbacks.
            for callback in self.callbacks:
                try:
                    callback.update_pixels(work_item)

                except:
                    logging.exception("Error passing work item to callback")

    # Standard method for queueing up a work item to the pool
    def queue_work_item(self, new_work_item):
        self.condition.acquire()
        self.queue.put([new_work_item.sequence_number, new_work_item])

        logging.debug("Queued work item: %d", new_work_item.sequence_number)
        logging.debug("Queue size now: %d", self.queue.qsize())

        self.condition.notify()
        self.condition.release()


