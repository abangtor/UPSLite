# UPSLite

## Start on external power

To start up the Raspberry Pi when the external power supply is connected,  
a small circuit is necessary, which is pulling down pin 3.  
A signal change of pin 3 initiates a wake up of the Pi if is halted.  
Additionally the two pads on the back of the UPS must be shorted.

Pin 3 is the I2C clock line.  
This means that if the external power is connected,  
there is no communication on the I2C interface possible.  
Due to that, the capacity of the battery can not be read during charging.

A possible solution for this flaw could be a circuit  
which is just shortly pulling down the line  
if the external power supply is connected.  
In my case, I can live with the draw back of the current solution.

### Circuit schematic
![StartupTriggerSchematic](img/StartupTriggerSchematic.drawio.svg)

### Sample implementation
![](img/StartupTrigger001.jpg)![](img/StartupTrigger002.jpg)

### BOM
| Ref | Qty | Part |
|:---:|:---:|:---- |
| R2  |  1  | Resistor 1.8 kΩ |
| T1  |  1  | NPN Transistor S9018 |
|  -  |  2  | Female Header 2 Pins |

## UPSLite Service

The UPSLite service is a small python script,  
which is regularly checking the power supply status,  
as also the battery level.

It will initiate a system shutdown if
- the battery capacity drops below 30%
- or the device is running more than 10 min on battery.

### Installation

* Move `UPSLite.py` to `/usr/local/bin/`
* Move `UPSLite.service` to `/etc/systemd/system/`
* To run, execute  
  `sudo systemctl start UPSLite.service`  
  `sudo systemctl enable UPSLite.service`

