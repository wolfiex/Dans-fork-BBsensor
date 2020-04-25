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

'''

