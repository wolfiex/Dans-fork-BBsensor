'''
Test the threading of the gps
'''



from . import *

print(gpio)

from threading import Thread,Lock
from datetime import datetime
import time

lock = Lock()

loc = Thread(target=bg_poll, args=(ser,lock), name='location_daemon')
loc.setDaemon(True)#bg
loc.start()

while True:
    time.sleep(7)
    
    #time in utc
    now = datetime.utcnow()
    print('Does not print from main. Use test script')
    
