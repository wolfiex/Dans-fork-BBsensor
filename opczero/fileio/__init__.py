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




### Failure on exit params
import sys

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

hooks = ExitHooks()
hooks.hook()




def onexit():
    f.close()

    import os
    if hooks.exit_code is not None:
        print("death by sys.exit(%d)" % hooks.exit_code)
    elif hooks.exception is not None:
        print("death by exception: %s" % hooks.exception)
    else:
        print("natural death")
        
        
    try:
        from ..R1 import alpha
        alpha.off()
    except Exception as e:
        print('OPC failure', e)
                
        
    print('rebooting')
    #os.system('sudo reboot')
    
import atexit
atexit.register(onexit)



