from .__init__ import sync
import sqlite3,os

filename = '/sensor.db'

# if we are root, write to root dir
user = os.popen('echo $USER').read().strip()


if user == 'root': __RDIR__ = '/root'
else: __RDIR__ = '/home/'+user

conn = sqlite3.connect(__RDIR__+filename)

SERIAL = os.popen('cat /sys/firmware/devicetree/base/serial-number').read()

sync(SERIAL, conn)
