from threading import Thread
import time

from gps import ser,lastloc
from R1 import alpha,info,poll
class combign:pass
#
# threading.Thread(target=self._thread_function, args=(arg,),
#                  kwargs={'arg2':arg2}, name='thread_function').start()

info(alpha)


print('############# Sleep 10 ############')
time.sleep(10)


alpha.on()

l=[]

for i in range(10):

    results = {}

    loc = Thread(target=lastloc, args=(ser,results), name='get location')
    loc.setDaemon(True)#bg
    loc.start()
    

    sensor = Thread(target=poll, args=(alpha,results), name='get location')
    sensor.start()

    loc.join()
    sensor.join()
    l.append(results)


alpha.off()

print(l)
