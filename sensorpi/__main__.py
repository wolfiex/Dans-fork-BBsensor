
#!/usr/bin/env/python3
# -*- coding: utf-8 -*-

"""
SensorPI LIBRARY

A library to run the portable sensors for the born in brandford project.

Project: Born In Bradford Breathes

Usage : python3 -m sensorpi

"""

__author__ = "Dan Ellis, Christopher Symonds"
__copyright__ = "Copyright 2020, University of Leeds"
__credits__ = ["Dan Ellis", "Christopher Symonds", "Jim McQuaid", "Kirsty Pringle"]
__license__ = "MIT"
__version__ = "0.8.1"
__maintainer__ = "D. Ellis"
__email__ = "D.Ellis@leeds.ac.uk"
__status__ = "Prototype"

# Built-in/Generic Imports
import time,sys,os,pickle, socket
from datetime import date,datetime
from re import sub



########################################################
##  Running Parameters
########################################################

## runtime constants
CSV = False
CONTINUOUS = True
DHT_module = False

hostname = socket.gethostname()
hostname = hostname.upper().lower()
if not "bbsensor" in hostname:   # For static sensor or serverpi, force continuous recording
    CONTINUOUS = True

# how long do we wait before polling a histogram (s)
SAMPLING_DELAY = 5

### hours (not inclusive)
NIGHT = [18,7]  # stop 07 - 6:59
SCHOOL = [9,15] # stop 10 - 2:59

#how often we save to file
SAMPLE_LENGTH_slow = 60*5
SAMPLE_LENGTH_fast = 60*1 # in seconds
SAMPLE_LENGTH = SAMPLE_LENGTH_fast
# assert SAMPLE_LENGTH > 10

if   "bbsensor" in hostname:
    TYPE   = 2 # { 1 = static, 2 = dynamic, 3 = server, 4 = home/school}
elif "bbstatic" in hostname:
    TYPE   = 1 # { 1 = static, 2 = dynamic, 3 = server, 4 = home/school}
elif "bbserver" in hostname:
    TYPE   = 3 # { 1 = static, 2 = dynamic, 3 = server, 4 = home/school}

DATE   = date.today().strftime("%d/%m/%Y")
STOP   = False
LAST_SAVE = None
LAST_UPDATE = None
LAST_UPLOAD = None
SERIAL = os.popen('cat /sys/firmware/devicetree/base/serial-number').read() #16 char key

########################################################
##  Imports
########################################################

## conditional imports
if DHT_module: from . import DHT

# Check Modules
from .tests import pyvers
from .SensorMod.log_manager import getlog
log = getlog(__name__)
print = log.print ## replace print function with a wrapper
log.info('########################################################'.replace('#','~'))

try:
    from .SensorMod import oled
    oled.standby(message = "   -- loading... --   ")
    OLED_module=True
except ImportError:
    OLED_module=False
log.info('USING OLED = %s'%OLED_module)

# initial GPS co-ordinates
from .SensorMod.gps.geolocate import lat,lon,alt
loc = {'gpstime':datetime.utcnow().strftime("%H%M%S"),'lat':lat,'lon':lon,'alt':alt}

# Exec modules
from .SensorMod.exitcondition import GPIO
from .SensorMod import power
from .crypt import scramble
if not CSV:
    from .SensorMod import db
    from .SensorMod.db import builddb, __RDIR__
else:
    log.critical('WRITING CSV ONLY')
    from .SensorMod.db import __RDIR__
    CSVfile = __RDIR__+'/simplesensor.csv'
    SAMPLE_LENGTH = SAMPLE_LENGTH_slow
    from pandas import DataFrame
    columns='SERIAL,TYPE,TIME,LOC,PM1,PM3,PM10,T,RH,BINS,SP,RC,UNIXTIME'.split(',')
    # inefficient I know, but it will only be used for testing
from .SensorMod import upload
from .SensorMod import gps
from .SensorMod import R1

########################################################
##  Setup
########################################################
gpsdaemon = gps.init(wait=False)
if not gpsdaemon and "bbsensor" in hostname:
    log.warning('NO GPS FOUND!')
    if OLED_module : oled.standby(message = "   -- NO GLONASS --   ")

try:
   alpha = R1.alpha
   log.info ("OPC found. Proceeding")
   OPC = True
except:
    OPC: False
    log.warning ("OPC library could not be imported")

if not OPC:
    if "bbsensor" in hostname or "bbstatic" in hostname:
        log.warning("No OPC present. Stopping program")
        STOP = True


loading = power.blink_nonblock_inf()



def interrupt(channel):
    log.warning("Pull Down on GPIO 21 detected: exiting program")
    global STOP
    STOP = True

GPIO.add_event_detect(21, GPIO.RISING, callback=interrupt, bouncetime=300)

log.info('########################################################')
log.info('starting {}'.format(datetime.now()))
log.info('########################################################')


if OPC: R1.clean(alpha)

while loading.isAlive():
    log.debug('stopping loading blink ...')
    power.stopblink(loading)
    loading.join(.1)


########################################################
## Check for pre-existing LAST_SAVE and LAST_UPDATE values
########################################################

if os.path.exists(os.path.join(__RDIR__,'.uploads')):
    with open (os.path.join(__RDIR__,'.uploads'),'r') as f:
        lines = f.readlines()
    for line in lines:
        if 'LAST_SAVE = ' in line:
            LAST_SAVE = line[12:].strip()
        elif 'LAST_UPDATE = ' in line:
            LAST_UPDATE = line[14:].strip()
        elif 'LAST_UPLOAD = ' in line:
            LAST_UPLOAD = line[14:].strip()
    if LAST_SAVE == None:
        with open (os.path.join(__RDIR__,'.uploads'),'a') as f:
            f.write('LAST_SAVE = None\n')
        LAST_SAVE = 'None'
    if LAST_UPDATE == None:
        with open (os.path.join(__RDIR__,'.uploads'),'a') as f:
            f.write('LAST_UPDATE = None\n')
        LAST_UPDATE = 'None'
    if LAST_UPLOAD == None:
        with open (os.path.join(__RDIR__,'.uploads'),'a') as f:
            f.write('LAST_UPLOAD = None\n')
        LAST_UPLOAD = 'None'
else:
    with open (os.path.join(__RDIR__,'.uploads'),'w') as f:
        f.write("LAST_SAVE = None\n")
        f.write("LAST_UPDATE = None\n")
        f.write("LAST_UPLOAD = None\n")
    LAST_SAVE = 'None'
    LAST_UPDATE = 'None'
    LAST_UPLOAD = 'None'

########################################################
## Main Loop
########################################################

def runcycle(SAMPLE_LENGTH):
    '''
    # data = {'SERIAL':SERIAL,
    #         'TYPE':TYPE,
    #         'TIME':now.strftime("%H%M%S"),
    #         'LOC' :scramble(('%s_%s_%s'%(lat,lon,alt)).encode('utf-8')),
    #         'PM1' :float(pm['PM1']),
    #         'PM3' :float(pm['PM2.5']),
    #         'PM10':float(pm['PM10']),
    #         'TEMP':float(pm['Temperature']),
    #         'RH'  :float(pm[  'Humidity' ]),
    #         'BINS':pickle.dumps([float(pm['Bin %s'%i]) for i in range(16)]),
    #         'SP':float(pm['Sampling Period']),
    #         'RC':int(pm['Reject count glitch']),
    #         'UNIXTIME': int(unixtime)
    #          }
    # Date,Type, Serial

    #(SERIAL,TYPE,d["TIME"],d["LOC"],d["PM1"],d["PM3"],d["PM10"],d["SP"],d["RC"],)
    '''
    global SAMPLING_DELAY

    results = []

    alpha.on()
    time.sleep(1)
    start = time.time()
    alpha.pm() # remove first value
    while time.time()-start < SAMPLE_LENGTH:
        now = datetime.utcnow()

        # sampling delay
        time.sleep(SAMPLING_DELAY) # keep as 1

        pm = alpha.histogram()
        #print(pm)
        if float(pm['PM1'])+float(pm['PM10'])  > 0:  #if there are results.

            if DHT_module: rh,temp = DHT.read()
            else:
                temp = pm['Temperature']
                rh   = pm[  'Humidity' ]


            if gpsdaemon : loc = gps.last.copy()
            else:
                if "bbsensor" in hostname: loc = dict(zip('gpstime lat lon alt'.split(),['000000','','','']))
                else: loc = {'gpstime':now.strftime("%H%M%S"),'lat':lat,'lon':lon,'alt':alt}

            unixtime = int(now.strftime("%s")) # to the second

            bins = pickle.dumps([float(pm['Bin %s'%i]) for i in range(16)])

            results.append( [SERIAL,
                             TYPE,
                             loc['gpstime'][:6],
                             scramble(('%(lat)s_%(lon)s_%(alt)s'%loc).encode('utf-8')),
                             float(pm['PM1']),
                             float(pm['PM2.5']),
                             float(pm['PM10']),
                             float(temp),
                             float(rh),
                             bins,
                             float(pm['Sampling Period']),
                             int(pm['Reject count glitch']),
                             unixtime,] )


            if OLED_module:
                now = str(datetime.utcnow()).split('.')[0]
                oled.updatedata(now,results[-1])

        if STOP:
            alpha.off()
            time.sleep(1)
            break


    alpha.off()
    time.sleep(1)# Let the rpi turn off the fan
    return results


########################################################
#Uploads and Syncs
########################################################

def rebuilddb(DATE):

    global LAST_SAVE

    cursor=db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list=[]
    for table_item in cursor.fetchall():
        table_list.append(table_item[0])

    for table_name in table_list:
        log.debug('Dropping table : {}'.format(table_name))
        db.conn.execute('DROP TABLE IF EXISTS ' + table_name)

    log.debug('rebuilding db')
    builddb.builddb(db.conn)

    log.info('Staging complete {} {}'.format(DATE, datetime.utcnow().strftime("%X")))

    with open (os.path.join(__RDIR__,'.uploads'),'r') as f:
        lines=f.readlines()
    with open (os.path.join(__RDIR__,'.uploads'),'w') as f:
        for line in lines:
            f.write(sub(r'LAST_SAVE = '+LAST_SAVE, 'LAST_SAVE = '+DATE, line))

    LAST_SAVE = DATE
    log.debug('LAST_SAVE = {}'.format(LAST_SAVE))

def upload_to_server(DATE):

    global LAST_SAVE

    if DATE != LAST_SAVE:
        log.debug('Uploading data to serverpi, hour={}'.format(hour))

        if upload.connected():
            if OLED_module: oled.standby(message = "   --  uploading  --   ")
            #check if connected to wifi
            loading = power.blink_nonblock_inf_update()
            ## SYNC
            try:
                upload_success = upload.sync(SERIAL,db.conn)
            except Exception as e:
                log.error("Error in attempting staging upload to serverpi - {}".format(e))
                upload_success = False
            if upload_success:
                rebuilddb(DATE)

            while loading.isAlive():
                power.stopblink(loading)
                loading.join(.1)

def update(DATE):

    global LAST_UPDATE
    global STOP

    if DATE != LAST_UPDATE:
        log.debug('Updating time and code, hour={}'.format(hour))

        if upload.online():

            ## update time!
            log.info(os.popen('sudo timedatectl &').read())

            ## run git pull
            log.debug('Checking git repo')
            branchname = os.popen("git rev-parse --abbrev-ref HEAD").read()[:-1]
            os.system("git fetch -q origin {}".format(branchname))
            if not (os.system("git status --branch --porcelain | grep -q behind")):
                STOP = True

            log.info('update complete {} {}'.format(DATE, hour))
            with open (os.path.join(__RDIR__,'.uploads'),'r') as f:
                lines=f.readlines()
            with open (os.path.join(__RDIR__,'.uploads'),'w') as f:
                for line in lines:
                    f.write(sub(r'LAST_UPDATE = '+LAST_UPDATE, 'LAST_UPDATE = '+DATE, line))

            LAST_UPDATE = DATE
            log.debug('LAST_UPDATE = {}'.format(LAST_UPDATE))

def stagedata(DATE):

    global LAST_SAVE

    if DATE != LAST_SAVE:
        if OLED_module: oled.standby(message = "   --  staging  --   ")
        #check if connected to wifi
        loading = power.blink_nonblock_inf_update()

        try:
            stage_success = upload.stage(SERIAL, __RDIR__)
        except Exception as e:
            log.error("Error in attempting staging serverpi data - {}".format(e))
            stage_success = False

        if stage_success:
            rebuilddb(DATE)

        while loading.isAlive():
            power.stopblink(loading)
            loading.join(.1)

def upload_to_external(DATE):

    global LAST_UPLOAD

    if upload.online():
        if DATE != LAST_UPLOAD:
            loading = power.blink_nonblock_inf_update()
            #check if connected to wifi
            ## SYNC
            try:
                upload_success = upload.upload()
            except Exception as e:
                log.error("Error in trying to upload data to external storage")
                log.error("Error message : {}".format(e))
                upload_success = False

            if upload_success:
                log.debug('upload complete on {}, hour = {}'.format(DATE, hour))

                with open (os.path.join(__RDIR__,'.uploads'),'r') as f:
                    lines=f.readlines()
                with open (os.path.join(__RDIR__,'.uploads'),'w') as f:
                    for line in lines:
                        f.write(sub(r'LAST_UPLOAD = '+LAST_UPLOAD, 'LAST_UPLOAD = '+DATE, line))

                LAST_UPLOAD = DATE

            else:
                log.debug('Upload failed on {}, hour = {}'.format(DATE, hour))

            while loading.isAlive():
                power.stopblink(loading)
                loading.join(.1)



########################################################
########################################################

'''
MAIN
'''

########################################################
## Run Loop
########################################################

SAMPLE_LENGTH=300 # initial sample set is only 10 seconds for db save debugging purposes. This then gets autoupdated within the relevant sections.

while True:
    #update less frequenty in loop
    # DATE = date.today().strftime("%d/%m/%Y")



    if SAMPLE_LENGTH>0:
        #alpha.on()
        #time.sleep(3)  
        power.ledoff()

        ## run cycle
        if OPC:
            d = runcycle(SAMPLE_LENGTH)

            ''' add to db'''
            if not CSV:
                if OLED_module: oled.standby(message = "   --  write db  --   ")
                db.conn.executemany("INSERT INTO MEASUREMENTS (SERIAL,TYPE,TIME,LOC,PM1,PM3,PM10,T,RH,BINS,SP,RC,UNIXTIME) \
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", d );
                db.conn.commit() # dont forget to commit!
                log.info('DB saved at {}'.format(datetime.utcnow().strftime("%X")))
            else:
                if OLED_module: oled.standby(message = "   --  write csv  --   ")
                DataFrame(d,columns=columns).to_csv(CSVfile,mode='a')
                log.info('CSV saved at {}'.format(datetime.utcnow().strftime("%X")))

            #if DEBUG:
                # if bserial : os.system("screen -S ble -X stuff 'sudo echo \"%s\" > /dev/rfcomm1 ^M' " %'_'.join([str(i) for i in d[-1]]))

        power.ledon()

    if STOP:
        alpha.off()
        time.sleep(1)
        break


    hour = datetime.now().hour

    if CSV:
        log.debug('CSV - skipping conditionals')

    elif CONTINUOUS:
        log.debug('continuous running')

        if (hour > SCHOOL[0]) and (hour < SCHOOL[1]):

            if OPC: alpha.off()
            time.sleep(1)

            DATE = date.today().strftime("%d/%m/%Y")

            log.debug('@ School, hour={}'.format(hour))
            ''' at school - try upload'''
            ''' rfkill block wifi; to turn it on, rfkill unblock wifi. For Bluetooth, rfkill block bluetooth and rfkill unblock bluetooth.'''

            if TYPE == 3:

                stagedata(DATE)

            else:

                upload_to_server(DATE)

                update(DATE)

        else:

            if OPC: alpha.off()
            time.sleep(1)

            DATE = date.today().strftime("%d/%m/%Y")

            if TYPE == 3:

                 upload_to_external(DATE)

                 update(DATE)

    else:
        if (hour > NIGHT[0]) or (hour < NIGHT[1]): #>18 | <7

            if OPC: alpha.off()
            time.sleep(1)

            ''' hometime - SLEEP '''
            log.debug('NightSleep, hour={}'.format(hour))
            if gpsdaemon and gpsdaemon.is_alive() == True: gps.stop_event.set() #stop gps
            power.ledon()
            SAMPLE_LENGTH = -1 # Dont run !  SAMPLE_LENGTH_slow
            if OLED_module: oled.standby()
            time.sleep(30*60) # sleep 0.5h
            TYPE = 4

        elif (hour > SCHOOL[0]) and (hour < SCHOOL[1]): # >7 <9 & >15 <18 utc (9-15)

            if OPC: alpha.off()
            time.sleep(1)

            DATE = date.today().strftime("%d/%m/%Y")

            log.debug('@ School, hour={}'.format(hour))
            ''' at school - try upload'''
            ''' rfkill block wifi; to turn it on, rfkill unblock wifi. For Bluetooth, rfkill block bluetooth and rfkill unblock bluetooth.'''

            if gpsdaemon and gpsdaemon.is_alive() == True: gps.stop_event.set() #stop gps

            upload_to_server(DATE)

            update(DATE)

            SAMPLE_LENGTH = SAMPLE_LENGTH_slow

            # sleep for 18 minutes - check break statement every minute


            if OLED_module: oled.standby()
            # check if we are trying to stop the device every minute
            for i in range(14):
                time.sleep(60) #5 sets of 5 min
                if STOP:break

            TYPE = 4

        else:

            if OPC: alpha.off()
            time.sleep(1)

            log.debug('en route - FASTSAMPLE, hour={}'.format(hour))

            if gpsdaemon: log.debug('GPS alive = {}'.format(gpsdaemon.is_alive()))

            if gpsdaemon and gpsdaemon.is_alive() == False:
                gpsdaemon = gps.init(wait=False)

            SAMPLE_LENGTH = SAMPLE_LENGTH_fast
            TYPE = 2


########################################################
########################################################


log.info('exiting - STOP: %s'%STOP)
if not CSV:
    db.conn.commit()
    db.conn.close()
power.ledon()
if OLED_module: oled.shutdown()
if not (os.system("git status --branch --porcelain | grep -q behind")):
    now = datetime.utcnow().strftime("%F %X")
    log.critical('Updates available. We need to reboot. Shutting down at %s'%now)
    os.system("sudo reboot")
