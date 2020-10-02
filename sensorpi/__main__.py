'''
SensorPI LIBRARY

A library to run the portable sensors for the born in brandford project.

Developers:
    D.Ellis CEMAC UOLeeds
    C.Symmonnds CEMAC UOLeeds
PIs:    
    K.Pringle UOLeeds
    J.McQuaid UOLeeds

'''
########################################################
##  Imports and constants
########################################################

import time,sys,os
from datetime import date,datetime

## runtime constants
DEBUG  = True
SERIAL = os.popen('cat /sys/firmware/devicetree/base/serial-number').read() #16 char key
DATE   = date.today().strftime("%d/%m/%Y")
STOP   = False
TYPE   = 2 # { 1 = static, 2 = dynamic, 3 = isolated_static, 4 = home/school}
LAST_SAVE = None

SAMPLE_LENGTH_slow = 60*2
SAMPLE_LENGTH_fast = 60*5 # in seconds
SAMPLE_LENGTH = SAMPLE_LENGTH_fast
# assert SAMPLE_LENGTH > 10

### hours (inclusive)
NIGHT = ['18','06']
SCHOOL = ['10','14']

########################################################
## Bluetooth setup
########################################################
# '''
# Start bluetooth DEBUG
# '''
# if DEBUG:
#     print('debug:', DEBUG)
#     try:
#         # Load watch command for bluetooth
#         # do this after 10 second delay from code to allow pi to finish booting.
#         bserial = True
#         os.system("screen -S ble -X stuff 'sudo rfcomm release rfcomm1 1 ^M' ")
#         os.system("screen -S ble -X stuff 'sudo rfcomm watch rfcomm1 1 & ^M' ")
#         # open('/dev/rfcomm1','w',1)
#         # bserial.write('starting')
#         # bserial.close()
#         print('debug using bluetooth serial: on')
#     except:print('no bluetooth serial')

########################################################
########################################################




########################################################
## Lib Imports
########################################################

from .tests import pyvers
# from .geolocate import lat,lon,alt
from .exitcondition import GPIO

from . import power
loading = power.blink_nonblock_inf()


from .crypt import scramble
from . import db
from . import upload
from . import DHT
from . import gps
loc = gps.init()
from . import R1
alpha = R1.alpha

def interrupt(channel):
    print ("Pull Down on GPIO 21 detected: exiting program")
    global STOP
    STOP = True

GPIO.add_event_detect(21, GPIO.RISING, callback=interrupt, bouncetime=300)

while loading.isAlive():
    if DEBUG: print('stopping loading blink ...')
    power.stopblink(loading)
    loading.join(.1)


########################################################
########################################################




########################################################
## Main Loop
########################################################

def runcycle():
    '''
    # data = {'TIME':now.strftime("%H%M%S"),
    #         'SP':float(pm['Sampling Period']),
    #         'RC':int(pm['Reject count glitch']),
    #         'PM1':float(pm['PM1']),
    #         'PM3':float(pm['PM2.5']),
    #         'PM10':float(pm['PM10']),
    #         'LOC':scramble(('%s_%s_%s'%(lat,lon,alt)).encode('utf-8'))
    #          }
    # Date,Type, Serial

    #(SERIAL,TYPE,d["TIME"],DATE,d["LOC"],d["PM1"],d["PM3"],d["PM10"],d["SP"],d["RC"],)
    '''
    
    results = []
    alpha.on()
    # for i in range(SAMPLE_LENGTH-1):
    start = time.time()
    while time.time()-start < SAMPLE_LENGTH:
        # now = datetime.utcnow()now.strftime("%H%M%S")
        #print(time.time()-start , SAMPLE_LENGTH)

        pm = R1.poll(alpha)
        
        if float(pm['PM1'])+float(pm['PM10'])  > 0:  #if there are results.
            rh,temp = DHT.read()
            loc     = gps.last.copy()
            
            # if DEBUG: print(rh,temp,loc)
            
            results.append( [SERIAL,TYPE,loc['gpstime'],DATE,scramble(('%s_%s_%s'%(loc['lat'],loc['lon'],loc['alt'])).encode('utf-8')),float(pm['PM1']),float(pm['PM2.5']),float(pm['PM10']),float(temp),float(rh),float(pm['Sampling Period']),int(pm['Reject count glitch']),] )

        if STOP:break
        time.sleep(.1) # keep as 1

    alpha.off()
    time.sleep(1)# Let the rpi turn off the fan
    return results


########################################################
########################################################


'''
MAIN
'''


print('starting',datetime.now())

R1.clean(alpha)

########################################################
## Run Loop
########################################################
while True:
    #update less frequenty in loop
    DATE = date.today().strftime("%d/%m/%Y")

    power.ledoff()
    ## run cycle
    d = runcycle()
    
    
    ''' add to db'''
    db.conn.executemany("INSERT INTO MEASUREMENTS (SERIAL,TYPE,TIME,DATE,LOC,PM1,PM3,PM10,T,RH,SP,RC) \
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", d );


    db.conn.commit() # dont forget to commit!
    
    
    #if DEBUG:
            # if bserial : os.system("screen -S ble -X stuff 'sudo echo \"%s\" > /dev/rfcomm1 ^M' " %'_'.join([str(i) for i in d[-1]]))
            
            # print('data',d)
    #             print(d[-1][2:3])
            
    power.ledon()
    
    if STOP:break
    
    
    hour = gps.last.copy()['gpstime'][:2]
    
    
    ''' Presume GPS always on as using as clock '''
        
    if hour > NIGHT[0] or hour < NIGHT[1]:
        ''' hometime - sample slowly '''
        SAMPLE_LENGTH = SAMPLE_LENGTH_slow
        time.sleep(60*18)
        TYPE = 4
        
    elif hour > SCHOOL[0] and hour < SCHOOL[1]:
        ''' at school - try upload'''
        if DATE != LAST_SAVE:
            if upload.online():
                
                loading = power.blink_nonblock_inf()
                upload.sync()
                while loading.isAlive():
                    power.stopblink(loading)
                    loading.join(.1)
                    
                print('upload complete', DATE, hour)
                LAST_SAVE = DATE

        SAMPLE_LENGTH = SAMPLE_LENGTH_slow
        
        # sleep for 18 minutes - check break statement every minute
        for i in range(18):
            time.sleep(60)
            if STOP:break
                
        TYPE = 4
    else: 
        ''' en route '''
        SAMPLE_LENGTH = SAMPLE_LENGTH_fast
        TYPE = 2
    
    

########################################################
########################################################


print('exiting- STOP:',STOP)
db.conn.commit()
db.conn.close()
power.ledon()
