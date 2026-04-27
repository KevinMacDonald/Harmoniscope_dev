# Sound Server Daemon

## Purpose

**(Hypothesis)** Plays pre-recorded `.wav` files in response to specific events from the `master-controller`. This is separate from the knob-to-MIDI sound generation.

## Communication
*   **(Hypothesis)** Listens for UDP packets from `master-controller` with instructions on which `.wav` file to play.