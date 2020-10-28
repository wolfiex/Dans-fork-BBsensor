'''
scripts to run if connected online
'''
import os

def online():

    cmd = '''
    PINGS=2
    TESTIP=8.8.8.8
    if ( ping -c $PINGS $TESTIP > /dev/null ) then
        echo "1"
    else
        echo "0"
    fi
    '''

    return int(os.popen(cmd).read())



def sync():

    # so something
    return True
