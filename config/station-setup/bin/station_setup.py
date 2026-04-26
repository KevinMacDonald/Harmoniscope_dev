#!/usr/bin/python3
# 
# Boot-time initialization script to configure the Pi based on the station
# ID selected in the DIP switches.
#

import ads1256
import jsmin
import json
import socket
import sys
import getopt
from subprocess import call
from os.path import dirname, isfile
from os import makedirs

# The file that contains the station configuration mappings.
STATION_CONFIG_FILE     = "/etc/harmoniscope/station-mappings.json"

# The template for the network interface configuration file.
NETWORK_CONFIG_TEMPLATE = "/etc/harmoniscope/eth0.template"

# The network configuration file to write.
NETWORK_CONFIG_FILE     = "/etc/network/interfaces.d/eth0"

# Where to write the station ID.
STATION_ID_FILE         = "/var/local/harmoniscope/station-id"


# Print out a usage statement and exit
def usage():
    print("Usage: ", __file__, " [options]")
    print("")
    print("  -h, --help               Print this help")
    print("  -c, --config-file=FILE   Use this station config file")
    print("  -i, --station-id=ID      Manually specify a station ID")
    print("  -n, --restart-network    Restart the network interfaces")
    print("  -d, --restart-daemons    Restart the station dameons")
    sys.exit(-1)

# Parse the command-line options
def parse_options(argv):
    options = {
        "station-config":   STATION_CONFIG_FILE,
        "restart-network":  False,
        "restart-daemons":  False
    }

    try:
        opts, args = getopt.getopt(argv,
                                    "hc:i:nd",
                                    [ 
                                        "help", 
                                        "config-file=",
                                        "station-id=", 
                                        "restart-network", 
                                        "restart-daemons"
                                    ])

    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-c", "--config-file"):
            options["station-config"] = arg
        if opt in ("-i", "--station-id"):
            options["station-id"] = arg
        if opt in ("-n", "--restart-network"):
            options["restart-network"] = True
        if opt in ("-d", "--restart-daemons"):
            options["restart-daemons"] = True
   
    return options 

# Load in the station configuration file.
def load_configuration(station_config):
    with open(station_config) as config_file:
        # Use JSMin to remove the comments in the config file.
        minified = jsmin.jsmin(config_file.read())

        # Parse the JSON into a Python object.
        config = json.loads(minified)
    return config

# This is old code. Now that the Waveshare board is gone, we can't read the ID that way. - Mike

# # Read in the station ID from the analog board.
# def read_station_id():
#     # We have to stop the control scan if it's running
#     if isfile("/var/run/control-scan.pid"):
#         call(["/bin/systemctl", "stop", "control-scan"])
#         restart_control_scan = True
#     else:
#         restart_control_scan = False
#
#     # Initialize the analog board.
#     ads1256.initialize()
#     ads1256.configure(ads1256.ADS1256_GAIN_1, ads1256.ADS1256_100SPS)
#
#     # Read in the analog input values
#     channels = ads1256.read_channels(4, 7, ads1256.ADS1256_INPUT_SINGLE_ENDED)
#
#     # Convert the values to a station ID. Greater than 2.5 volts is a set value.
#     station_id =
#     for value in channels:
#         station_id <<= 1
#         if value > 2.5:
#             station_id |= 1
#
#     # Restart the control-scan if we stopped it.
#     if restart_control_scan:
#         call(["/bin/systemctl", "start", "control-scan"])
#
#     return str(station_id)

# Configure the IP address based on the station ID.
def set_ip_address(config, options):
    ip_address = config["stations"][options["station-id"]]["ip_address"]

    # Read in the template configuration and fill in the IP address..
    with open(NETWORK_CONFIG_TEMPLATE) as f:
        config_text = f.read().replace('%IP_ADDRESS%', ip_address)

    # Write out the configuration file.
    with open(NETWORK_CONFIG_FILE, "w") as f:
        f.write(config_text) 

    # Restart the interface to pick up the new address.
    if options["restart-network"]:
        print("Restarting network interfaces...")
        call(["/sbin/ifdown", "eth0"])
        call(["/sbin/ifup",   "eth0"])

    return ip_address

# Configure the hostname based on the IP address
def set_hostname(ip_address):
    hostname = socket.gethostbyaddr(ip_address)[0]
    call(["/bin/hostname", hostname])

# Configure which daemons will start based on the station ID.
def configure_daemons(config, options):
    for daemon in config["daemons"]:
        if options["station-id"] in daemon["runs_on_stations"]:
            print("Enabling daemon: ", daemon["name"])
            call(["/bin/systemctl", "enable", daemon["name"]])

            if options["restart-daemons"]:
                call(["/bin/systemctl", "start", daemon["name"]])

        else:
            print("Disabling daemon: ", daemon["name"])
            call(["/bin/systemctl", "disable", daemon["name"]])

            if options["restart-daemons"]:
                call(["/bin/systemctl", "stop", daemon["name"]])


##
## Begin main code
##

def main(argv):
    print("Configuring station...")

    # Parse the command-line options.
    options = parse_options(argv)

    # Load the configuration.
    config = load_configuration(options["station-config"])


    # Old code that used the Waveshare

    # # Read in the station ID from the DIP switches
    # if 'station-id' not in options:
    #     options["station-id"] = read_station_id()
    #     print("Station ID: ", options["station-id"])
    # else:
    #     print("Station ID overridden to: ", options["station-id"])
    #
    # # Write out the station ID so that other processes can find it.
    # makedirs(dirname(STATION_ID_FILE), 0o755, True)
    # with open(STATION_ID_FILE, "w") as f:
    #     f.write(options["station-id"])

    if options["station-id"] not in config["stations"]:
        print("No configuration found for station ID ", options["station-id"])
        sys.exit(-1)

    # Set the IP address
    ip_address = set_ip_address(config, options)

    # Set the hostname
    set_hostname(ip_address)

    # Enable the appropriate daemon processes
    configure_daemons(config, options)

    print("Station configuration done!")

##
## End main code
##

# Glue code to call the main() function.
if __name__ == "__main__":
   main(sys.argv[1:])
