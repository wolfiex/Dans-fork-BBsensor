'''
If we do not already have a database (or wish to delete and replace the existing one) run

python -m serverpi.db new
            or
python -m serverpi.db + user input

'''

import os,sys,sqlite3
from .__init__ import __RDIR__,filename,conn

## no accidental overwrites
if 'new' not in sys.argv:
    assert 'yes' == input('Please type "yes" to delete the old database (if it exists) and create a new one')


#remove and create new
conn.close()
os.system('rm '+__RDIR__+filename)
conn = sqlite3.connect(__RDIR__+filename)

#ID INTEGER PRIMARY KEY AUTOINCREMENT,
conn.execute('''
CREATE TABLE MEASUREMENTS
         (
          SERIAL       CHAR(16)    NOT NULL,
          TYPE         INT         NOT NULL,
          TIME         CHAR(6)     NOT NULL,
          DATE         CHAR(8)     NOT NULL,
          LOC          BLOB        NOT NULL,
          PM1          REAL        NOT NULL,
          PM3          REAL        NOT NULL,
          PM10         REAL        NOT NULL,
          T            REAL        NOT NULL,
          RH           REAL        NOT NULL,
          SP           REAL        NOT NULL,
          RC           INT         NOT NULL
);
''')

conn.execute('''
CREATE TABLE PUSH
         (
          SERIAL       CHAR(16)    NOT NULL,
          TIME         CHAR(6)     NOT NULL,
          DATE         CHAR(8)     NOT NULL
);
''')


conn.commit()
conn.close()
print('A new database has now been created')

 #
 # [str(i) for i in (location['gpstime'],location['lat'],location['lon'],location['alt'],int(location['nsat']),location['PM1'],location['PM2.5'],location['PM10'])]
