# Harmoniscope Debugging Log

## Objective

To modify the Harmoniscope project for standalone operation on a single Raspberry Pi, with the primary goal of having physical knob movements trigger the playback of specific `.wav` files.

## Summary of Experiments

### Phase 1: System & Installation Stabilization

*   **Experiment 1.1: Standalone Configuration**
    *   **Actions:** Hardcoded `station-id` to '3' in `station_setup.py`. Modified `station-mappings.json` to run all daemons on station 3 and use `127.0.0.1` for all communication.
    *   **Observation:** The system now correctly identifies as a single, self-contained station.

*   **Experiment 1.2: Fixing Package Management**
    *   **Actions:** Modified `install.sh` to point `apt` to the `legacy.raspbian.org` archives for Jessie.
    *   **Observation:** `apt-get update` now succeeds.

*   **Experiment 1.3: Fixing Python Dependencies**
    *   **Actions:** Modified `install.sh` to use a bootstrap script to install a working, period-appropriate version of `pip`. Created `requirements.txt` to pin `flask` and `jsmin` to known-good versions.
    *   **Observation:** Python dependencies now install reliably. The installation process is now stable and reproducible.

### Phase 2: Audio Subsystem Debugging

*   **Experiment 2.1: Initial Audio Test (`sound_test.py`)**
    *   **Actions:** Created a standalone script to play a `.wav` file using `simpleaudio`.
    *   **Observation:** The script was often silent or reported "Device or resource busy".
    *   **Conclusion:** Other processes were interfering with the sound card.

*   **Experiment 2.2: Identifying Audio Conflicts**
    *   **Actions:** Used `fuser -v /dev/snd/*` to identify processes using the audio hardware.
    *   **Observation:** Identified `fluidsynth` and `pulseaudio` as culprits.
    *   **Actions:** Masked `fluidsynth` service. Removed `pulseaudio` package.
    *   **Conclusion:** The audio device is no longer being hijacked by non-Harmoniscope services.

*   **Experiment 2.3: Robust ALSA Configuration**
    *   **Actions:** Created `/etc/asound.conf` to configure the default audio device. Iterated on this file.
    *   **Observation:** Using `type hw` was unreliable. Using `type plughw` was better but still failed due to permissions.
    *   **Final Action:** Configured `asound.conf` to use a `dmix` software mixer. This allows multiple applications to share the sound card without conflict. Added `ipc_perm 0666` to resolve the final permission error.
    *   **Conclusion:** The ALSA audio layer is now stable. `sound_test.py` works reliably after a reboot.

## Current Status
The base OS and ALSA audio system are stable and correctly configured. We can reliably play `.wav` files from a standalone Python script. The application-level logic remains untested. The original "howling" sound is no longer present, likely because the conflicting audio servers have been removed.

## Phase 3: Application Logic & MIDI

*   **Experiment 3.1: Document Hardware**
    *   **Action:** Created placeholder documentation for all known hardware components (`SOUND_CARD.md`, `AMPLIFIER.md`, `SPEAKER.md`, `ANALOG_IO.md`).
    *   **Observation:** This provides a structured place to record hardware details.

### Next Proposed Experiment (3.2)

**Hypothesis:** The knobs generate MIDI events, which are intended to be synthesized by `fluidsynth`.

**Test:** Re-enable `fluidsynth` and use a MIDI monitoring tool (`aseqdump`) to see if knob movements generate MIDI data.