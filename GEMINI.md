# Gemini AI Instructions

- Read all markdown files in this directory.
- Keep markdown files updated as we progress.

We are working with existing hardware and software. The original raspberry pi, analog IO board, sound card, amplifier, speaker etc. are all in use and powered up with this pi. To start off we will hack the startup code to hardcode a station name for this pi. According to the original station-mappings.json the pi in use here is 'station3'. We should modify startup code such that this pi believes it is station3 independent of its current IP address since a new IP address was assigned to all SSH and SFTP to work. 

The purpose of this project is to take the existing code and make the modifications necessary to allow a single pi to operate standalone, with no other devices. We are re-purposing all existing hardware and software.
