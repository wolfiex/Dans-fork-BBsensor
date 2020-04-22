import spidev
import opc
from time import sleep

spi = spidev.SpiDev()
spi.open(0, 0)

spi.mode = 1
spi.max_speed_hz = 500000


#wait a bit.
sleep(1.0)
try:
	alpha = opc.OPCR1(spi)
except Exception as e:
	print ("Startup Error: {}".format(e))
print (alpha)

print (alpha.on())
sleep(10)

#alpha.fan_on()
print("Read info string")
print(alpha.read_info_string())

print("Read serial number")
print(alpha.sn())

print("Read firmware")
print(alpha.read_firmware())


print("Read config")
print(alpha.read_config())


print("Read Histogram")
print(alpha.histogram())

sleep(10)
print("Read PM")
print(alpha.pm())


alpha.off()
