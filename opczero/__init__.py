from threading import Thread,Lock
from datetime import datetime
import time,re
from . import power

###########################
## Loading
###########################

# loading blinks
loading = power.blink_nonblock_inf()


from . import fileio,gps
from .R1 import alpha,info,poll,keep

# checks interval (seconds)
# results are sampled every 30 seconds, sample atleast 2
FAST_DURATION = 1*60
assert FAST_DURATION >= 60 

move = [0]*10
counter = 0
clean = re.compile('[\{\}]')


###########################
## OPC test 
###########################

print('write',fileio.f)

info(alpha)

print('############# SampleHist. ############')
print(poll(alpha))

print('############# GPS daemon ############')
lock = Lock()
loc = Thread(target=gps.bg_poll, args=(gps.ser,lock), name='location_daemon')
loc.setDaemon(True)#bg
loc.start()



#stop blinking
time.sleep(2)
while loading.isAlive():
    print('stopping loading blink ...')
    power.stopblink(loading)
    loading.join(.1)

print('############# BEGIN ############')



###########################
## Functions
###########################



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
        

    alpha.off()
    end_geo = gps.latlon()
    return res, [abs(end_geo[i] - start_geo[i])**2 for i in [0,1]]



###########################
## RunScript
###########################



while True:
    power.ledoff()
    while gps.last == None:
        print('waiting for gps result')
        time.sleep(4)
        continue
        
    data,diff = fastsample()
    
    
    
    
    power.ledon()
    fileio.f.write(bytes(clean.sub('',data),"utf-8"))
    print(diff)
    

