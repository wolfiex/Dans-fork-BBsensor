# BBSensor

Program for running data collection in the BornInBradford BREATHES project, using Raspberry Pi based sensors.

This Repository can be used for data collection on a portable sensor, a static sensor or a hub server.

## Power Led meaning:
- Led on whist sampling
- Led off when writing to file
- blink 1s on loading code
- blink 3 seconds on upload  (sending data)

## Setup

### If setting up a serverpi:
Full instructions are here:
https://raspap.com/#quick

```
sudo apt-get update
sudo apt-get full-upgrade
sudo reboot
```
Then, set the WiFi country and hostname (if not already set) in raspi-config's Localisation Options:
`sudo raspi-config`

Finally, run
`curl -sL https://install.raspap.com | bash`

RaspAP wifi network will be set up, with default SSID and password which can be changed through the browser GUI.

### seting up logger
`bash setup/opc_install.sh`

#### Then run the relevant tests
`cd sensorpi && python3 runtests.py`

## link .rc_local to run on boot
Open `sudo nano /etc/rc.local`
and source the local rc file in this directory.

For testing this will likely be under `/home/pi/BBSensor/rc.local` but will eventually NEED to be changed to the `/root` folder when deployed permanently.

We add the lines:

`bash /home/pi/BBSensor/rc.local ``
or
` bash /root/BBSensor/rc.local `

### rc.local contents

This contains:
- network clock updates on load (takes a number of seconds)
- code to run measurement unit on boot
- server init


## Create a new database
`python -m sensorpi.SensorMod.db new`

### Debug corruption on device

```
find .git/objects/ -size 0 -exec rm -f {} \;
git fetch origin

git reset --hard origin/
```
