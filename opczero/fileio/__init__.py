
# output file   
f = open('./results.csv','ba')



def onexit():
    f.close()
    from R1 import alpha
    alpha.off()
    
    
import atexit
atexit.register(onexit)