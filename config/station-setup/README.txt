Tool that runs on boot to configure the station based on the ID selected on 
the analog input DIP switches. The etc/harmoniscope/station-mappings.json
configuration file specifies which stations do what.

Installation: 

    sudo ./install.sh

How it works:

The etc/init.d/station-setup script gets installed to run at boot time, before
the network interfaces are configured. It is a Linux-conformant init script,
which just wraps the bin/station_setup.py program.

The station setup program first reads the values of the station ID jumpers
using the analog interface, and converts those into a station ID (0-15). 

The etc/harmoniscope/station-mappings.json configuration file maps those
station IDs to IP addresses, and also which processes (daemons) should be 
run for that station.

IP address is configured by taking a template file (which is 
etc/harmoniscope/eth0.template) and filling in the IP address for the given
station ID. It also sets the hostname appropriately for the station. The
etc/hosts file that gets install contains the static list of station IP 
addresses and names.

Each daemon needs to have it's own init.d script (see the control-scan for
an example of how it works). The station setup tool will selectively enable
or disable these scripts at boot time according to the station mappings.

Testing:

You can manually run the station_setup.py script to try out different 
station configurations. Run it with the '--help' parameter to get usage
instructions.

