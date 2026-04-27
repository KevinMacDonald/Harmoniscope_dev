# Analog I/O Board

## Details

*   **Model:** (e.g., Waveshare High-Precision AD/DA Board)
*   **Type:** Analog-to-Digital / Digital-to-Analog converter.
*   **Notes:** This board reads the voltage from the physical knobs. The `control-scan` daemon communicates with this board to get the knob positions. The original method for reading a station ID from DIP switches on this board is commented out in `station_setup.py`.