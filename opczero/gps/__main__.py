'''
Test the threading of the gps
'''



import gps
from threading import Thread,Lock
from datetime import datetime,timezone
import time

lock = Lock()


loc = Thread(target=gps.bg_poll, args=(gps.ser,lock), name='location_daemon')
loc.setDaemon(True)#bg
loc.start()

while True:
    time.sleep(7)
    
    #time in utc
    now = datetime.utcnow()
    print(now,gps.last['gpstime'],now.timestamp(),gps.last)
    