'''
RPI sensor code.

sudo nano /etc/rc.local
sudo python3 /home/pi/BBSensor/opczero/shutdown.py
cd /home/pi/BBSensor && sudo python3 -c 'import opczero;opczero.run()'  >> /root/sensor.log &


'''



from threading import Thread,Lock
from datetime import datetime
import time,re,sys,os
from . import power
import signal,sys,time
terminate = False

DEBUG = True #os.environ['DEBUG'] =='TRUE'
print('debug:', DEBUG)





def signal_handling(signum,frame):
    global terminate
    print('termination signal ctrl + c')
    terminate = True

signal.signal(signal.SIGINT,signal_handling)


if sys.version[0] != '3':
    sys.exit('Unfortunately this code was written for py3k, \n feel free to update it through on https://github.com/wolfiex/BBSensor')


###########################
## Loading
###########################

# loading blinks
loading = power.blink_nonblock_inf()
time.sleep(10)
from . import fileio,gps
from .R1 import alpha,info,poll,keep

if DEBUG:
    try:
        # Load watch command for bluetooth
        # do this after 10 second delay from code to allow pi to finish booting.
        bserial = True
	os.system("pkill -9 screen")
        os.system("screen -S ble -X stuff 'sudo rfcomm release rfcomm1 1 ^M' ")
        os.system("screen -S ble -X stuff 'sudo rfcomm listen rfcomm1 1 & ^M' ")
        # open('/dev/rfcomm1','w',1)
        # bserial.write('starting')
        # bserial.close()
        print('debug using bluetooth serial: on')
    except:print('no bluetooth serial')


# save interval (seconds)

'''sample interval - how long to run before saving'''
SAVE_INTERVAL = 10#2*60


#assert SAVE_INTERVAL >= 20
print ('SAVE_INTERVAL:',SAVE_INTERVAL,'s' )

move = [0]*10
counter = 0
clean = re.compile('[\{\}]')


###########################
## OPC test
###########################

print('write',fileio.f)

info(alpha)

print('############# SampleHist. ############')
alpha.on()
time.sleep(1)
test = poll(alpha)
print(test)
# if bserial:os.system('sudo -u pi echo "%s" > /dev/rfcomm1'% str(test))
del test
alpha.off()

print('############# GPS daemon ############')
lock = Lock()
loc = Thread(target=gps.bg_poll, args=(gps.ser,lock), name='location_daemon')
loc.setDaemon(True)#bg
loc.start()



#stop blinking
time.sleep(10)
while loading.isAlive():
    print('stopping loading blink ...')
    power.stopblink(loading)
    loading.join(.1)

print('############# BEGIN ############')



###########################
## Functions
###########################



def fastsample():
    '''
    sample at 1hz (sleep 1) and save every SAVE_INTERVAL
    '''
    global terminate
    start = datetime.utcnow()
    #start_geo = gps.latlon()
    res = ''
    elapsed = 0

    alpha.on()
    print('on')
    while elapsed < SAVE_INTERVAL:

        now = datetime.utcnow()
        elapsed = (now-start).seconds

        time.sleep(5)
        location = gps.last.copy()
        #sensor read
        sensor = poll(alpha)

        # merge
        for k in keep: location[k] = sensor[k]
        location['utc']= str(now)

        res += str(location)+'\n'
        if terminate: break


    alpha.off()
#    time.sleep(1)
    print('sensor')
    #end_geo = gps.latlon()
    return res, [str(i) for i in (location['gpstime'],location['lat'],location['lon'],location['alt'],int(location['nsat']),location['PM1'],location['PM2.5'],location['PM10'])]   #, [abs(end_geo[i] - start_geo[i])**2 for i in [0,1]]



###########################
## RunScript
###########################


def run(repeat = 1e99):
    power.ledoff()
    while gps.last == {'gpstime':None}:
        print('waiting for gps result')
        time.sleep(4)
        continue

    print('start')

    for i in range(int(repeat)):
        power.ledoff()
        data ,last = fastsample()
        power.ledon()
        if DEBUG:
            if bserial : os.system("screen -S ble -X stuff 'sudo echo \"%s\" > /dev/rfcomm1 ^M' " %'_'.join(last))
            print('data',data,last ,i)
        fileio.f.write(bytes(clean.sub('',data),"utf-8"))
        if terminate: break
        time.sleep(1)
