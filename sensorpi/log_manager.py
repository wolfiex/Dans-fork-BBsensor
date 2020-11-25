'''
The logging file
'''

import logging

if user == 'root': __RDIR__ = '/root'
else: __RDIR__ = '/home/'+user

logfile = __RDIR__+'/sensor.log'


console_level = logging.INFO


def getlog(name):
  '''
  Function to set up a new logger for each module
  '''

  log = logging.getLogger(name) ## if running interactively with ipython, replace this with a descriptive string
  log.setLevel(logging.DEBUG)

  '''
  Console Stream
  '''
  console = logging.StreamHandler()
  formatter = logging.Formatter('%(levelname)-10s  %(message)s')
  console.setFormatter(formatter)
  console.setLevel(console_level)
  log.addHandler(console)


  '''
  File Debug
  '''
  tofile = logging.FileHandler(logfile, mode='a')
  formatter = logging.Formatter('%(asctime)s ~ %(name)s ~ %(levelname)s ~ %(message)s')
  tofile.setFormatter(formatter)
  tofile.setLevel(logging.DEBUG)
  log.addHandler(tofile)
  
  return log
