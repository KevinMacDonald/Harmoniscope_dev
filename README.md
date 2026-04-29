# Harmoniscope

## Purpose

The Harmoniscope project was originally a distributed, multi-station interactive art installation featuring lights, MIDI sounds, and networked hardware running on Raspbian Jessie.

The current iteration of this codebase represents a **Standalone Conversion**. The goal of this conversion was to repurpose the legacy code and hardware to run a single, self-contained prop unit without relying on external network requests, light servers, or external synthesizers.

## The Puzzle
Now that we have a station working standalone and knob changes are playing sounds, we want to create a puzzle that the user must solve. Here is a proposal:
- The system reads in the 'sounds' collection for each knob, and creates an in-memory collection that is randomized and assigns those to the 8 knob positions.
- Each in-memory collection contains one sound that starts with 'stationzap'. The objective is to turn each knob to the position where 'stationzap*' plays. Because the  in-memory randomized collection is being used, that position will change from one solving of the puzzle to the next.
- When each knob is placed where 'stationzap*' plays then the system will play the 'arrival_processed.wav' file, followed by the 'maineventstations.wav'. 
- Upon completion of the 'maineventstations.wav' file playing, the in-memory sound collections are randomized again and re-assigned to all knob positions. This concludes
the puzzle, and the knobs are now reset for the next solution of the puzzle. 


## Standalone Architecture

The system has been heavily modified to operate offline on a single Raspberry Pi. It is hardcoded to identify internally as **Station 3**.

### Hardware Components
* **Raspberry Pi**: Running legacy Raspbian Jessie.
* **AB Electronics IO Pi Plus**: An I2C analog-to-digital converter board that reads the physical knob sweeps.
* **USB Sound Card & Amplifier**: A standard USB audio interface (configured via `dmix` in `/etc/asound.conf`) feeding a physical amplifier and speaker.

### Active Software Daemons
Because this is a standalone sound-only prop, the software stack has been significantly trimmed. Only the following native daemons are active:

1. **`control-scan`**: Polls the IO Pi Plus board via the I2C bus for the physical positions of the four analog knobs. Transmits these values to the `master-controller`.
2. **`master-controller`**: The brain of the system. Tracks the logical position of the knobs against a target victory configuration. When a knob moves, it translates the physical position into a `.wav` file request according to `/etc/harmoniscope/controller_config.json`.
3. **`sound-server`**: A Flask-based web service utilizing the `simpleaudio` library. It receives HTTP requests from the `master-controller` and instantly plays the specified `.wav` files out of the USB sound card.

### Disabled Services
To prevent conflicts, network timeouts, and audio highjacking, several original services have been disabled or stubbed out:
* **`light-server`**: Network calls to the light server inside `update_pixel.py` have been stubbed out. This allows the system to process lighting animations rapidly in memory without suffering HTTP timeouts.
* **`fluidsynth` & `pulseaudio`**: Disabled and uninstalled, respectively. The system no longer synthesizes MIDI notes.

## Configuration

Sound assignments are managed in `/etc/harmoniscope/controller_config.json`. 

Each knob on Station 3 possesses an array of `sounds` mapping physical integer positions (0-7) directly to file names in the `/usr/local/share/harmoniscope/sounds/` directory (excluding the `.wav` extension).

## Installation & Service Management

To deploy code changes and restart the daemon services, run the main installation script as root:

```bash
sudo ./install.sh
```

If you need to manually check logs to ensure the components are communicating:
* `tail -f /var/log/harmoniscope/control-scan.log`
* `tail -f /var/log/harmoniscope/master-controller.log`
* `tail -f /var/log/harmoniscope/sound-server.log`