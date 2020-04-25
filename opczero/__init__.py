from threading import Thread,Lock
from datetime import datetime
import time


import gps
from R1 import alpha,info,poll,keep
import fileio
#
# threading.Thread(target=self._thread_function, args=(arg,),
#                  kwargs={'arg2':arg2}, name='thread_function').start()

# checks interval (seconds)
FAST_DURATION = 5*60
assert FAST_DURATION >= 60 # results are sampled every 30 seconds, sample atleast 2




info(alpha)

print('############# SampleHist. ############')
print(poll(alpha))

print('############# Sleep 10 ############')



lock = Lock()
loc = Thread(target=gps.bg_poll, args=(gps.ser,lock), name='location_daemon')
loc.setDaemon(True)#bg
loc.start()

time.sleep(10)


'''
delete /var/lib/bluetooth/xx:xx:xx:xx:xx:xx/config file.
Edit /etc/bluetooth/main.conf(For ex: Name=%d-%h to Name=abcd-5)
service bluetooth restart.
'''




def fastsample():
    start = datetime.utcnow()
    start_geo = gps.latlon()
    res = ''
    alpha.on()
    elapsed = 0

    while elapsed < FAST_DURATION:
        
        now = datetime.utcnow()
        elapsed = (now-start).seconds
        
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
    
    while gps.last == None:
        print('waiting for gps result')
        time.sleep(4)
        continue
        
    data,diff = fastsample()
    fileio.f.write(bytes(data,"utf-8"))
    print(data,diff)
    

