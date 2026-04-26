# workitem.py - implementation of the light server work item class

# WorkItem provides a unit of state change for the light control system
# It contains a pixel number and a set of r,g,b,w values for that pixel
# The work item is queued up to the worker thread where it is handled
# In the future it can be extended with other use cases (such as all on,
# all off, or more complex patterns)

from threading import Lock

class WorkItem:
    # Static member variables - shared between instances
    s_lock            = Lock()
    s_sequence_number = 0

    def __init__(self, pixels, red, green, blue, white, paint):
        # Make sure the pixel number is sane.
        self.pixels = pixels
        assert(len(self.pixels) > 0)
        for pixel in self.pixels:
            assert(pixel >= 0)

        # Copy the work item details over.
        self.red   = int(red)
        self.green = int(green)
        self.blue  = int(blue)
        self.white = int(white)
        self.paint = int(paint)

        # Increment the work item sequence number, using the lock to avoid
        # thread contention.
        with WorkItem.s_lock:
            WorkItem.s_sequence_number += 1
            self.sequence_number = WorkItem.s_sequence_number

