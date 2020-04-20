import os 

serial = os.popen('cat /proc/cpuinfo | grep --ignore-case serial').read()

'''
If exists, append last updated 
else update hostname after being allocated a number
'''


