# events/event.py - A base class Event type.

class Event:
    def __lt__(self, other):
        return self.when < other.when

    def __eq__(self, other):
        return self.when == other.when and self.type == other.type
