'''
Get GPS values from usb
'''

import serial

#find usb gps
for i in range(10):
    try:# each unplug registers as a new number, we dont expect more than 10 unplugs without a restart
        ser = serial.Serial('/dev/ttyACM%d'%i)
        print( 'Connected serial on /dev/ttyUSB%d'%i)
        break
    except:continue


def lastloc(ser,result):
    ser.write(bytes("ATI\r\n", "utf-8"));
    while True:
        last = ''
        for byte in ser.read(s.inWaiting()): last += chr(byte)
        if len(last) > 0:
            # Do whatever you want with last
            result['location']=bytes(last, "utf-8")
            print (bytes(last, "utf-8"))
            last = ''
