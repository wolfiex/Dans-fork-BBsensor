'''
RPI sensor code. 

sudo nano /etc/rc.local

cd /home/pi/BBSensor && sudo python3 -c 'import opczero;opczero.run()'  >> /root/sensor.log &


'''



from threading import Thread,Lock
from datetime import datetime
import time,re,sys
import power

if sys.version[0] != '3':
    sys.exit('Unfortunately this code was written for py3k, \n feel free to update it through on https://github.com/wolfiex/BBSensor')


###########################
## Loading
###########################

# loading blinks
loading = power.blink_nonblock_inf()
time.sleep(4)
import fileio,gps


# checks interval (seconds)
# results are sampled every 30 seconds, sample atleast 2
FAST_DURATION = 15

move = [0]*10
counter = 0
clean = re.compile('[\{\}]')


###########################
## OPC test 
###########################

print('write',fileio.f)


print('############# GPS daemon ############')
lock = Lock()
loc = Thread(target=gps.bg_poll, args=(gps.ser,lock), name='location_daemon')
loc.setDaemon(True)#bg
loc.start()



#stop blinking
time.sleep(3)
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

    print('on')
    while elapsed < FAST_DURATION:

        now = datetime.utcnow()
        elapsed = (now-start).seconds

        time.sleep(2)
        #gps global
        location = gps.last.copy()
        #sensor read

        location['utc']= str(now)

        res += str(location)+'\n'


    end_geo = gps.latlon()
    return res, [abs(end_geo[i] - start_geo[i])**2 for i in [0,1]]



###########################
## RunScript
###########################


def run(repeat = 1e99):
    power.ledoff()
    while gps.last == {'gpstime':None}:
        print('waiting for gps result')
        time.sleep(4)
        #continue

    print('start')
    
    for i in range(int(repeat)):
        power.ledoff()
        data,diff = fastsample()
        power.ledon()
        print('data:',data)
        fileio.f.write(bytes(clean.sub('',data),"utf-8"))
        time.sleep(1)
        print(diff)
    
    
run(10)

