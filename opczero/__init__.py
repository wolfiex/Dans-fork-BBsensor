from threading import Thread,Lock
from datetime import datetime
import time


import fileio
import gps,power
from R1 import alpha,info,poll,keep

#
# threading.Thread(target=self._thread_function, args=(arg,),
#                  kwargs={'arg2':arg2}, name='thread_function').start()

# checks interval (seconds)
FAST_DURATION = 1*60
assert FAST_DURATION >= 60 # results are sampled every 30 seconds, sample atleast 2
move = [0]*10
counter = 0

print('write',fileio.f)



info(alpha)

print('############# SampleHist. ############')
print(poll(alpha))

print('############# Sleep 10 ############')



lock = Lock()
loc = Thread(target=gps.bg_poll, args=(gps.ser,lock), name='location_daemon')
loc.setDaemon(True)#bg
loc.start()

# 10 second delay and blink - 
power.blink(10)

'''
delete /var/lib/bluetooth/xx:xx:xx:xx:xx:xx/config file.
Edit /etc/bluetooth/main.conf(For ex: Name=%d-%h to Name=abcd-5)
service bluetooth restart.
'''




def fastsample():
    start = datetime.utcnow()
    start_geo = gps.latlon()
    res = ''
    elapsed = 0

    alpha.on()
    while elapsed < FAST_DURATION:
        
        
        now = datetime.utcnow()
        elapsed = (now-start).seconds
        
        time.sleep(10)
        #gps global
        location = gps.last.copy()
        #sensor read
        sensor = poll(alpha)
        
        # merge
        for k in keep: location[k] = sensor[k]
        location['utc']= now
        
        res += str(location)+'\n'
        
        #print(location)
        #print(now,gps.last['gpstime'],now.timestamp(),gps.last)
        

    alpha.off()
    end_geo = gps.latlon()
    return res, [abs(end_geo[i] - start_geo[i])**2 for i in [0,1]]







while True:
    power.ledoff()
    while gps.last == None:
        print('waiting for gps result')
        time.sleep(4)
        continue
        
    data,diff = fastsample()
    
    
    
    
    power.ledon()
    fileio.f.write(bytes(data,"utf-8"))
    print(data,diff)
    

