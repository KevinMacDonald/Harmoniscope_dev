Daemon which runs on an ongoing basis, scanning the control inputs and sending
updates to the master control service. It must run as root, because it accesses
the ADC.

Note that this depends on the 'requests' Python module:

    sudo pip3 install requests

Installation:

    sudo ./install.sh

Testing:

There's a mock master control service in the 'test' directory. Run it, and 
then run the daemon with the options to connect to localhost:

   test/master_mock.py &
   bin/control_scan.py -m localhost

