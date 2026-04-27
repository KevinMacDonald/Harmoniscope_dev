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
    *   **Action:** Created placeholder documentation for all known hardware components (`SOUND_CARD.md`, `AMPLIFIER.md`, `SPEAKER.md`, `ANALOG_IO.md`). User populated files with model numbers.
    *   **Observation:** This provides a structured place to record hardware details.

*   **Experiment 3.2: Re-enable `fluidsynth` and Test Permissions**
    *   **Action:** Unmasked and started the `fluidsynth` service. Ran `sound_test.py` as the `pi` user.
    *   **Observation:** `fluidsynth` started successfully as `root`. The `sound_test.py` script failed with `Permission denied` when trying to create the IPC semaphore for `dmix`.
    *   **Conclusion:** This confirms that when a `root` process starts the mixer, other users cannot access it by default.

### Next Proposed Experiment (3.3)
*   **Experiment 3.4: Isolate the Howling Process**
    *   **Action:** After a reboot (with howling), stopped `sound-server`.
    *   **Observation:** The howling stopped immediately.
    *   **Action:** Stopped `fluidsynth`, then restarted `sound-server`.
    *   **Observation:** The howling did not return. The `sound_test.py` script worked correctly.
    *   **Conclusion:** The `sound-server` is the source of the noise, but it is only triggered when `fluidsynth` is also running. This points to an unwanted event from the `master-controller` that the `sound-server` is misinterpreting.

### Next Proposed Experiment (3.5)

**Hypothesis:** The knobs generate MIDI events, which are intended to be synthesized by `fluidsynth`.

**Test:**
1.  Temporarily disable the `sound-server` by modifying `station-mappings.json` so we can test the rest of the system without interference.
2.  Run `install.sh` to apply the change.
3.  Use the `aseqdump` utility to monitor for MIDI events while turning a physical knob.

*   **Experiment 3.5.1: MIDI Monitoring Test**
    *   **Action:** Ran `aseqdump -p "FLUID Synth"`.
    *   **Observation:** Command failed with `Invalid port FLUID Synth - No such file or directory`.
    *   **Conclusion:** The client name "FLUID Synth" is incorrect. We need to find the correct client name.

*   **Experiment 3.5.2: List MIDI Clients**
    *   **Action:** Ran `aseqdump -l` to list all available MIDI clients.
    *   **Observation:** The output did not contain an entry for `FLUID Synth`.
    *   **Conclusion:** The `fluidsynth` service is not running or has failed to connect to the ALSA MIDI subsystem.

### Next Proposed Experiment (3.5.3)

*   **Experiment 3.5.3: Check `fluidsynth` Status**
    *   **Action:** Ran `sudo systemctl status fluidsynth`.
    *   **Observation:** The service was `inactive (dead)`. The logs show it had started and then stopped at some point after the last `install.sh` run.
    *   **Conclusion:** The `fluidsynth` service is not running, which is why it did not appear in the MIDI client list.

*   **Experiment 3.5.4: Manually Start `fluidsynth`**
    *   **Action:** Ran `sudo systemctl start fluidsynth` and then `aseqdump -l`.
    *   **Observation:** The service reported as `active (running)`, but it did not appear in the list of ALSA MIDI clients.
    *   **Conclusion:** The `fluidsynth` process is starting, but it is failing to connect to the ALSA MIDI subsystem. This likely points to an internal configuration problem.

### Next Proposed Experiment (3.5.5)

*   **Experiment 3.5.5: Examine `fluidsynth` Configuration**
    *   **Action:** Ran `cat /etc/fluidsynth/config.txt`.
    *   **Observation:** The configuration file contains the line `set audio.alsa.device dmixer0`.
    *   **Conclusion:** This is incorrect. Our `asound.conf` defines the software mixer as `dmixer`. This name mismatch is preventing `fluidsynth` from connecting to the audio hardware.

*   **Experiment 3.5.6: Correct `fluidsynth` Configuration**
    *   **Action:** Used `sed` to change `dmixer0` to `dmixer` in `/etc/fluidsynth/config.txt`. Restarted the service with `systemctl restart fluidsynth`. Ran `aseqdump -l`.
    *   **Observation:** The `fluidsynth` client is still not present in the MIDI client list.
    *   **Conclusion:** Correcting the audio device name was necessary, but it was not sufficient. The service is still failing to initialize its MIDI port for another reason.

*   **Experiment 3.5.7: Check `fluidsynth` Status After Config Fix**
    *   **Action:** Ran `sudo systemctl status fluidsynth`.
    *   **Observation:** The service reports as `active (running)`.
    *   **Conclusion:** This confirms the service process is running, but it is not correctly connected to the ALSA MIDI subsystem. The problem is not that it's failing to start, but that it's failing to initialize properly while it's running.

### Next Proposed Experiment (3.5.8)

*   **Experiment 3.5.8: Analysis of Architecture**
    *   **Action:** User proposed an alternative hypothesis based on the project's custom `.wav` files.
    *   **New Hypothesis:** The primary mechanism for knob-to-sound interaction is NOT MIDI. Instead, the `master-controller` receives knob data and sends a command to the `sound-server` to play a specific `.wav` file. `fluidsynth` may be used for a different purpose or not at all in the standalone configuration.
    *   **Conclusion:** This is a very strong hypothesis that better explains the project's file structure and the `sound-server`'s existence. We will pivot to test this new theory.

### Next Proposed Experiment (3.6)

*   **Experiment 3.6: Test `sound-server` Hypothesis**
    *   **Action:** User advised a change in direction, focusing on the original bundled code (`simpleaudio`) rather than system-level tools (`fluidsynth`).
    *   **Conclusion:** This is a much stronger approach. We will pivot to an application-centric investigation.

## Phase 4: Application-Centric Debugging

*   **Experiment 4.1: Revert ALSA Configuration**
    *   **Action:** Per user direction, reverted `/etc/asound.conf` to a simpler `plughw` configuration, removing the `dmix` software mixer to adhere more closely to the original system state.
    *   **Hypothesis:** The `sound-server` is the sole audio handler and does not need to share the audio device.

### Next Proposed Experiment (4.2)

**Hypothesis:** The `sound-server` daemon contains the logic for playing sounds. The original "howling" was caused by this daemon misinterpreting a startup event.

**Test:**
1.  Apply the simplified `asound.conf` and reboot to ensure a clean state.
2.  Ensure `fluidsynth` remains disabled.
3.  Ensure `sound-server` is enabled in `station-mappings.json`.
4.  Run `install.sh` to start the services.
5.  Analyze the code for `apps/sound/sound_server.py` to understand its intended behavior and find the source of the howl.

*   **Experiment 4.2: Strategic Decision on `asound.conf`**
    *   **Action:** User proposed reverting `asound.conf` to its original state (i.e., deleting it).
    *   **Decision:** We will keep the current `plughw` configuration in `/etc/asound.conf`.
    *   **Reasoning:** The original state (no config file) caused the OS to default to the wrong sound card (the built-in one). The current configuration is a minimal, period-appropriate fix that correctly directs audio to the USB sound card. It is a necessary hardware configuration step, not a modification of the application's logic.

### Next Proposed Experiment (4.3)

**Hypothesis:** The `sound-server` daemon contains the logic for playing sounds. The original "howling" was caused by this daemon misinterpreting a startup event.

**Test:** Analyze the code for `apps/sound/sound_server.py` to understand its intended behavior and find the source of the howl.

*   **Experiment 4.3: Strategic Decision on `fluidsynth`**
    *   **Action:** User questioned the role of `fluidsynth` in the current plan.
    *   **Decision:** We will proceed with `fluidsynth` disabled for this phase of testing.
    *   **Reasoning:** To test the hypothesis that the `sound-server` is the primary audio component, we must first isolate it from other potential audio sources like `fluidsynth`. This simplifies the system and allows us to test one component at a time. If the `sound-server` proves to be the correct path, `fluidsynth` may not be needed at all for the standalone configuration. If not, we will re-evaluate its role.

### Next Proposed Experiment (4.4)

**Hypothesis:** The `sound-server` daemon contains the logic for playing sounds. The original "howling" was caused by this daemon misinterpreting a startup event.

**Test:** Analyze the code for `apps/sound/sound_server.py` to understand its intended behavior and find the source of the howl.

*   **Experiment 4.4: Analyze `sound_server.py`**
    *   **Action:** Analyzed the code for `apps/sound/bin/sound_server.py`.
    *   **Observation:** The script is a simple launcher. It does not contain any audio playback or web server logic itself. It imports and instantiates two key classes: `SoundPlayer` and `WebService` from a `sound` library module.
    *   **Conclusion:** The core application logic, and therefore the source of the howling bug, must be within the `SoundPlayer` or `WebService` classes.

### Next Proposed Experiment (4.5)

**Hypothesis:** The `SoundPlayer` class contains the audio playback logic that is causing the howl, likely when it receives a malformed request from the `WebService`.

**Test:** Analyze the code for `apps/sound/lib/sound/sound_player.py` and `apps/sound/lib/sound/web_service.py`.

*   **Experiment 4.5: Analyze `sound_player.py` and `web_service.py`**
    *   **Action:** Analyzed the provided source code.
    *   **Observation:** The `SoundPlayer` class has a hard dependency on `fluidsynth`. The `initialize_midi_player` method throws a fatal exception if it cannot find a MIDI port with "FLUID" in the name.
    *   **Conclusion:** This is the root cause of the `sound-server` crash loop when `fluidsynth` is disabled. The server is not robust to this condition.

### Next Proposed Experiment (4.6)

**Hypothesis:** Making the MIDI initialization in `sound_player.py` non-fatal will allow the `sound-server` to run correctly without `fluidsynth`, enabling us to test `.wav` playback in isolation.

**Test:**
1.  Apply the proposed robustness changes to `sound_player.py`.
2.  Ensure `fluidsynth` is disabled.
3.  Run `sudo ./install.sh` to copy the new code and restart the `sound-server`.
4.  Use a command-line tool (`curl`) to directly send a "play sound" request to the running `sound-server` and listen for audio.

*   **Experiment 4.6: Strategic Decision on `pulseaudio`**
    *   **Action:** User questioned the status of the other service we disabled, `pulseaudio`.
    *   **Decision:** We will proceed with `pulseaudio` removed from the system.
    *   **Reasoning:** `PulseAudio` is a sound server that is not part of the original Harmoniscope project. It was identified as a source of conflict because it intercepts audio, preventing applications like `sound-server` from directly and reliably accessing the ALSA hardware. Removing it was a necessary system simplification step to create a stable audio environment.

### Next Proposed Experiment (4.7)

**Hypothesis:** Making the MIDI initialization in `sound_player.py` non-fatal will allow the `sound-server` to run correctly without `fluidsynth`, enabling us to test `.wav` playback in isolation.

**Test:**
1.  Apply the proposed robustness changes to `sound_player.py`.
2.  Ensure `fluidsynth` is disabled.
3.  Run `sudo ./install.sh` to copy the new code and restart the `sound-server`.
4.  Use a command-line tool (`curl`) to directly send a "play sound" request to the running `sound-server` and listen for audio.