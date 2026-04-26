import pyaudio
import wave
import sys

from threading import Thread

CHUNK = 20480

class WavPlayer(Thread):
    def __init__(self, file_name, device = None):
        Thread.__init__(self)
        self.daemon = True

        self.file_name = file_name
        self.device    = device


    def run(self):
        wf = wave.open(self.file_name, 'rb')

        self.sample_width = wf.getsampwidth()
        self.channels     = wf.getnchannels()
        self.framerate    = wf.getframerate()

        # instantiate PyAudio (1)
        p = pyaudio.PyAudio()

        # open stream (2)
        stream = p.open(format   = p.get_format_from_width(self.sample_width),
                        channels = self.channels,
                        rate     = self.framerate,
                        output   = True,
                        output_device_index = self.device)

        # play stream (3)
        data = wf.readframes(CHUNK)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(CHUNK)

        # stop stream (4)
        stream.stop_stream()
        stream.close()

        # close PyAudio (5)
        p.terminate()

