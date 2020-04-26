'''
power

sudo tee
'''
import os,time
os.system('echo none | sudo tee /sys/class/leds/led0/trigger')


def ledon():
    os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness')
    
def ledoff():
    os.system('echo 1 | sudo tee /sys/class/leds/led0/brightness')
    
def blink(n = 4 ):
    for i in range(n):
        ledon()
        time.sleep(1)
        ledoff()

def blink_nonblock(n=4):
    from threading import Thread
    loc = Thread(target=blink, args=(n), name='blink')
    loc.start()
    loc.join(n)





'''
power

Turn off power to all USB ports (must use port 2):
sudo uhubctl -p 2 -a 0
Turn on power to all USB ports (must use port 2):
sudo uhubctl -p 2 -a 1
Turn off power to Wifi+Ethernet (must use port 1):
sudo uhubctl -p 1 -a 0
Note that Raspberry Pi 4 is very different from previous models as it has USB3 chip. It doesn't support turning off power to Wifi+Ethernet, and for USB you will need to use something like that to turn off (must use port 4):

sudo uhubctl -l 2 -p 4 -a 0



Zero

Can you turn the interface tx power off using iwconfig? That should save a fair bit.



iwconfig wlan0 txpower off
iwconfig wlan0 txpower auto






echo none | sudo tee /sys/class/leds/led0/trigger
echo 1 | sudo tee /sys/class/leds/led0/brightness

power led






echo 0 | sudo tee /sys/devices/platform/soc/20980000.usb/buspower >/dev/null
sleep 10
echo 1 | sudo tee /sys/devices/platform/soc/20980000.usb/buspower >/dev/null


I'm also turning off the HDMI by doing this:
Code: Select all

/usr/bin/tvservice -o


'''

