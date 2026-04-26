# Harmoniscope

## Purpose

See details below taken from SSH on a pi. 
pi@hscope-dev:~/harmoniscope $ cat /etc/os-release
PRETTY_NAME="Raspbian GNU/Linux 8 (jessie)"
NAME="Raspbian GNU/Linux"
VERSION_ID="8"
VERSION="8 (jessie)"
ID=raspbian
ID_LIKE=debian
HOME_URL="http://www.raspbian.org/"
SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"

The purpose of this project is to take the existing code and make the modifications necessary to allow a single pi to operate standalone, with no other devices.  
We are re-purposing all existing hardware and software. The original raspberry pi, analog IO board, sound card, amplifier, speaker etc. are all in use and
powered up with this pi. To start off we will hack the startup code to hardcode a station name for this pi. According to the original station-mappings.json the
pi in use here is 'station3'. We should modify startup code such that this pi believes it is station3 independent of its current IP address since a new IP address
was assigned to all SSH and SFTP to work. 


## Overview

Harmoniscope appears to be a multi-station system, likely running on Raspberry Pi devices, designed for an interactive experience involving lights, sound, and physical controls.

The system is composed of several components as defined in `config/station-setup/etc/harmoniscope/station-mappings.json`:
*   **Master Controller**: The central process that coordinates station states and generates events.
*   **Light Server**: Controls lighting based on events from the master controller.
*   **Sound Server**: Controls audio based on events from the master controller.
*   **Control Scan**: Reads input from physical controls (like knobs) and sends them to the master controller.

## Station Setup

Each station in the Harmoniscope network is configured at boot time. The `station_setup.py` script runs, which:
1.  Requires a station ID to be passed to it.
2.  Assigns a static IP address to the station based on its ID.
3.  Sets the station's hostname.
4.  Enables or disables specific daemons (services) based on the station's role.

## Installation

To install the full Harmoniscope suite on a device, run the main installation script as root:

```bash
sudo ./install.sh
```

This script installs dependencies, copies over all the necessary application files, and then runs the station configuration script.

---

(This is a stub file. Please expand on these sections with more detail about the project architecture, goals, and operation.)