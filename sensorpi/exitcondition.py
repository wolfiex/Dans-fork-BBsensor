'''
Ensure we can do a controlled exit when pressing ctrl+c
'''
### Failure on exit params
import sys,time,datetime,traceback
import RPi.GPIO as GPIO
from .log_manager import getlog
log = getlog(__file__)

'''
test script for hardware interrupt
Connect the bottom right pin (GPIO 21) to ground (bottom left) and then release
'''

# for GPIO numbering, choose BCM
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)




'''
On Hard Exit
'''

class ExitHooks(object):
    def __init__(self):
        self.exit_code = None
        self.exception = None

    def hook(self):
        self._orig_exit = sys.exit
        sys.exit = self.exit
        sys.excepthook = self.exc_handler

    def exit(self, code=0):
        self.exit_code = code
        self._orig_exit(code)

    def exc_handler(self, exc_type, exc, *args):
        self.exception = exc
        log.critical("".join(traceback.format_exception(exc_type, exc, *args)))

hooks = ExitHooks()
hooks.hook()


def onexit():
    import os
    if hooks.exit_code is not None:
        log.critical("death by sys.exit(%d)" % hooks.exit_code)
    elif hooks.exception is not None:
        log.critical("death by exception: %s" % hooks.exception)
        
    else:
        log.critical("natural death")

    log.print('Attempting to exit in a controlled Manner \n',datetime.datetime.now(),'\n')


    from . import R1
    try : R1.alpha.off()
    except:None
    from . import db
    try:db.conn.commit()
    except db.sqlite3.ProgrammingError: None
    try:db.conn.close()
    except:None
    try:
        from . import gps
        gps.pinoff()
    except:None
    from . import power
    power.ledoff()
    power.ledon()
    sys.exit('Ending Python')

import atexit
atexit.register(onexit)
