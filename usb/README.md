# The alternative data transfer mode. 

## Setup new usb 
1. Plug in USB
2. run `python3 setup_USB.py`
3. copy UUID code
4. place in `BBSensor/usb/approved.dev` on github repo to be disemminated to all devices

## File location 
Files are transfered into the `/transferdata` directory on your USB. 

## Authentication
Checksum that the encryption file on the usb matches that on the device
Only transfers if the UUID is part of the approved files list
The correct path must exist

## Program
Checks attached devices, 
mounts them and checks authentication. 
If this passes it copies the files 

## Leds
Off whilst writing
On when finished



# Bootup setup
This has been added to rc.local.
Move `optional_usb.rules` into `/etc/udev/rules.d/`



