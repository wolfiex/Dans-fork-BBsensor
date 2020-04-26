'''
fileio
'''


# output file   
__RDIR__ = '/root'
f = open(__RDIR__+'/results.csv','ba')#ba
print('results at '+__RDIR__+'/results.csv')


def onexit():
    f.close()
    try:
        from R1 import alpha
        alpha.off()
    except:
        print('OPC failure')
    import os
    print('rebooting')
    os.system('sudo reboot')
    
import atexit
atexit.register(onexit)



