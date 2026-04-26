Light controller web server and associated utilities

Installation:

    sudo ./install.sh

Testing:

Run it with --help to get options:

   bin/light_server.py --help

The light server requires the OLA libraries to be installed, which can be
a bit complex, see:

  https://3.basecamp.com/3186135/buckets/234952/documents/69398434

If OLA is not installed, the DMX interface will not run. You can still
run the simulator with the '-s' option.

    bin/light_server.py -s

