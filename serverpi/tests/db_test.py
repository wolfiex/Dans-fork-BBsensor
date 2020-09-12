import os
os.system('rm test.db')

import sqlite3

conn = sqlite3.connect('test.db')

conn.execute('''
CREATE TABLE HELLOWORLD
         (ID INT PRIMARY KEY     NOT NULL,
         NAME           TEXT    NOT NULL,
         NSAT         INT     NOT NULL,
         LON        CHAR(50),
         PM1         REAL);

''')

conn.execute("INSERT INTO HELLOWORLD (ID,NAME,NSAT,LON,PM1) \
      VALUES (1, 'PiZero', 3, 'CaliforniaDreamingEncrypted', 20000.00 )");

conn.execute("INSERT INTO HELLOWORLD (ID,NAME,NSAT,LON,PM1) \
      VALUES (2, 'Pi3', 66, 'DiscoInfernoEncrypted', 111.00 )");



# read

cursor = conn.execute("SELECT id, name, nsat, pm1 from HELLOWORLD")
for row in cursor:
   print (row)


# cursors empties when iterated
cursor = conn.execute("SELECT id, name, nsat, pm1 from HELLOWORLD")


assert list(cursor)[0][1] == 'PiZero'

print('SQLdb PASSED') 


import os
os.system('rm test.db')
