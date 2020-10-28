'''
SERVERPI LIBRARY

D.Ellis CEMAC
C.Symonds CEMAC
K.Pringle UOL
J.McQuaid UOL

'''

## imports
import time,sys,os
from datetime import date,datetime

## runtime constants
DEBUG = True
SERIAL = os.popen('cat /sys/firmware/devicetree/base/serial-number').read() #16 char key
DATE = date.today().strftime("%d/%m/%Y")
STOP = False
TYPE=1# { 1 = static, 2 = dynamic, 3 = isolated_static}
SAMPLE_LENGTH = 10 # in seconds

# SAMPLE_SLEEP = 0#60*.5#(15-1) # in seconds
#assert SAMPLE_SLEEP > 10


## lib imports
from .tests import pyvers
from .geolocate import lat,lon,alt
from . import R1
#from R1 import alpha,info,poll,keep
alpha = R1.alpha
from .exitcondition import GPIO
from .crypt import scramble
from . import db

def interrupt(channel):
    print ("Pull Down on GPIO 21 detected: exiting program")
    global STOP
    STOP = True

GPIO.add_event_detect(21, GPIO.RISING, callback=interrupt, bouncetime=300)


'''
rpi serial number as hostname
'''

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
    for i in range(SAMPLE_LENGTH-1):
        now = datetime.utcnow()

        pm = R1.poll(alpha)

        if DEBUG: print(pm)

        if float(pm['PM1'])+float(pm['PM10'])  > 0:
            # if there are no results.
            results.append( [SERIAL,TYPE,now.strftime("%H%M%S"),DATE,scramble(('%s_%s_%s'%(lat,lon,alt)).encode('utf-8')),float(pm['PM1']),float(pm['PM2.5']),float(pm['PM10']),float(pm['Sampling Period']),int(pm['Reject count glitch']),] )

        if STOP:break
        time.sleep(1) # keep as 1

    alpha.off()
    time.sleep(1)# Let the rpi turn off the fan
    return results

'''
MAIN
'''


print('starting')

R1.clean(alpha)
while True:
    #update less frequenty in loop
    DATE = date.today().strftime("%d/%m/%Y")
    d = runcycle()

    db.conn.executemany("INSERT INTO MEASUREMENTS (SERIAL,TYPE,TIME,DATE,LOC,PM1,PM3,PM10,SP,RC) \
          VALUES (?,?,?,?,?,?,?,?,?,?)", d );

    db.conn.commit() # dont forget to commit!
    if STOP:break



print('exiting- STOP:',STOP)
db.conn.commit()
db.conn.close()
