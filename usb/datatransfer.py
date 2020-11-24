'''
copy files if approved
'''

import os,re,glob
os.system('echo none | sudo tee /sys/class/leds/led0/trigger')

def ledon():
    os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness > /dev/null')
    
def ledoff():
    os.system('echo 1 | sudo tee /sys/class/leds/led0/brightness > /dev/null')
    
SERIAL = os.popen('cat /sys/firmware/devicetree/base/serial-number').read() #16 char key
PEM = glob.glob('/root/BBSensor/s*pi/crypt/encrypt.pem')[0]
DBs = glob.glob('/root/s*.db')


checksum = 'b50ef6e46fec55460787f2b86fb59a099ec78a98'
uuids = tuple(open('/root/BBSensor/usb/approved.dev','r'))

usbs = []

for u in os.popen('sudo blkid').readlines():
    loc = [u.split(':')[0]]
    if '/dev/sd' not in loc[0]: continue
    loc+=re.findall(r'"[^"]+"',u)
    columns = ['loc']+re.findall(r'\b(\w+)=',u)
    
    usbs.append(dict(zip(columns,loc)))
    
    
    
for u in usbs:
    
    print ('Connecting to %(LABEL)s'%u)

    os.system('sudo umount /media')
    os.system('sudo mount %(loc)s /media'%u)
    
    if u['UUID'] not in uuids:
        print('UUID not allowed: %(UUID)s - %(LABEL)s'%u)
        continue
    if not os.path.exists('/media/transferdata'): 
        print('FAILED on %(LABEL)s'%u)
        continue
    if checksum != os.popen('shasum /media/transferdata/encrypt.pem').read().split(' ')[0]:
        print ('CHECKSUM did not match - check /media/transferdata/encrypt.pem')
        continue
    
    ledoff()
    
    for db in DBs:
        dname = db.rsplit('/',1)[-1]
        print('Transferring',dname)
        os.system('cp -n %s /media/transferdata/%s_%s'%(db,SERIAL[:16],dname))# -n for no clobber
        

    os.system('sudo umount /media')

    
ledon()
print('--end--')
