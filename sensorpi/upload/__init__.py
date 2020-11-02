'''
scripts to run if connected online
'''
import os
from datetime import date,datetime

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


def sync(SERIAL,conn):

    DATE = date.today().strftime("%d%m%Y")
    TIME = datetime.utcnow().strftime("%H%M%S")

    data = [(SERIAL,TIME,DATE,)]

    conn.executemany("INSERT INTO PUSH (SERIAL,TIME,DATE) VALUES(?, ?, ?);", data )

    conn.commit()

    

    return True
