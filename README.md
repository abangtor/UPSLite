# UPSLite

Python script for Raspberry Zero UPS-Lite.

This script will shutdown the device when the battery capacity drops below 30%.

## Installation

* Move `UPSLite.py` to `/usr/local/bin/`

* Move `UPSLite.service` to `/etc/systemd/system/`

* To run on system start, execute

  `sudo systemctl start UPSLite.service`

  `sudo systemctl enable UPSLite.service`

