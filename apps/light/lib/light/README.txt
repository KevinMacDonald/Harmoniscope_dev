Light controller libraries.

constants.py:       Shared constant values.
dmx.py:             DMX interface wrapper.
light_simulator.py: A GUI simulator for the lights connected via DMX.
web_service.py:     The web service implementation.
worker.py:          Consumer thread, takes work items from the web service
                    and passes them on to the DMX and simulator instances.
workitem.py:        A class for encapsulating a light change work item.
