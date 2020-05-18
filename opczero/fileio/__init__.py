'''
fileio
'''
import os
user = os.popen('echo $USER').read().strip()

# output file   
if user == 'root': __RDIR__ = '/root'
else: __RDIR__ = '/home/'+user


from datetime import date
__FILE__ = date.today().strftime("/results_%d_%m_%Y.csv")


f = open(__RDIR__+__FILE__,'ba')#ba
print('results at '+__RDIR__+__FILE__)


def onexit():
    f.close()
    try:
        from ..R1 import alpha
        alpha.off()
    except Exception as e:
        print('OPC failure', e)
    import os
    ##print('rebooting')
    ##os.system('sudo reboot')
    
import atexit
atexit.register(onexit)



