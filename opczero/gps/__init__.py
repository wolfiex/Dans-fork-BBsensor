'''
Get GPS values from usb
'''

import serial,time

last = None
ser = None
gpio = True



def connect():
    global ser,gpio
    if gpio:
        ser = serial.Serial('/dev/ttyS0')
    else:   
        for i in range(10):
            try:# each unplug registers as a new number, we dont expect more than 10 unplugs without a restart
                #try:ser = serial.Serial('/dev/ttyAMA%d'%i)
                #except:
                ser = serial.Serial('/dev/ttyACM%d'%i)

                print( 'Connected serial on /dev/ttyACM%d'%i)
                break
            except:continue


def bg_poll(ser,lock):
        global last
        #ignored values to be named utc
        params = 'utc gpstime lat utc lon utc fix nsat HDOP alt utc WGS84 utc lastDGPS utc utc'.split()
        while True:
                try:
                    line = str(ser.readline())
                except serial.SerialException:
                    print('lost connection - reconnecting')
                    #last = {}
                    connect()
                    time.sleep(5)
                    
                    continue
                    
                
                if line.find('GGA') > 0: 
                    lock.acquire()
                    last = dict(zip(params,line.split(',')))
                    lock.release()
                    
                                    
def latlon():
    global last
    if last['lat']=='' or last['lon']=='':
        return [0,0]
    else: 
        return [float(last['lat']),float(last['lon'])]





#find usb gps
connect()
