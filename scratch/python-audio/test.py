#!/usr/bin/env python3

from wav_player import WavPlayer

a = WavPlayer("/home/pi/harmoniscope/apps/sound/sounds/cow_toy.wav", 0)
b = WavPlayer("/home/pi/harmoniscope/apps/sound/sounds/timer.wav", 1)
c = WavPlayer("/home/pi/harmoniscope/apps/sound/sounds/boing_x.wav", 1)

a.start()
b.start()
c.start()

while True:
    foo = None
