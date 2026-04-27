# Master Controller Daemon

## Purpose

**(Hypothesis)** The central "brain" of the project. It likely coordinates all other daemons.

## Communication
*   **(Hypothesis)** Listens for UDP packets from `control-scan` containing knob data.
*   **(Hypothesis)** Generates MIDI events (for `fluidsynth`) and/or sound events (for `sound-server`) based on knob positions.