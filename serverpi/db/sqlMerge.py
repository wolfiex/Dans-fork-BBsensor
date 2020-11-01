import sqlite3,os

class sqlMerge(object):
    """Basic python script to merge data of 2 !!!IDENTICAL!!!! SQL tables"""

    def __init__(self):

        self.db_a = None
        self.db_b = None

    def merge(self, file_a, file_b):
        
        self.db_a = sqlite3.connect(file_a)

        cursor_a = self.db_a.cursor()
        cursor_a.execute("SELECT name FROM sqlite_master WHERE type='table';")

        table_list=[]
        for table_item in cursor_a.fetchall():
            table_list.append(table_item[0])
        
        cursor_a = self.db_a.cursor()
        
        cmd = "attach ? as toMerge"
        cursor_a.execute(cmd, (file_b, ))
        
        for table_name in table_list:

            new_table_name = table_name + "_new"

            try:
                cmd = "CREATE TABLE IF NOT EXISTS {0} AS SELECT * FROM {1};".format(new_table_name,table_name)
                cursor_a.execute(cmd)
                       
                cmd = "INSERT INTO {0} SELECT * FROM toMerge.{1};".format(new_table_name,table_name)
                cursor_a.execute(cmd)

                cursor_a.execute("DROP TABLE IF EXISTS " + table_name);
                cursor_a.execute("ALTER TABLE " + new_table_name + " RENAME TO " + table_name);        
                
                self.db_a.commit()

            except sqlite3.OperationalError:
                print("ERROR!: Merge Failed for " + new_table_name)
                cursor_a.execute("DROP TABLE IF EXISTS " + new_table_name);

            finally:
                if table_name == table_list[-1]:
                    cmd = "detach toMerge"
                    cursor_a.execute(cmd, ())
                    self.db_a.close()

        return
    
    def mergelist(self, file_a, merge_list):
        
        try:
            assert type(merge_list) == list
        except (AssertionError):
            print ('Failed assertion to ensure merge files are a list')
            raise
        except:
            print ('Unexpected Error')
            raise
            
            try:
                assert os.path.exists(file_a)
            except (AssertionError):
                print ('Failed assertion to ensure master file exists')
                raise
            except:
                print ('Unexpected Error')
                raise
            
        for file in merge_list:
            
            try:
                assert os.path.exists(file)
            except (AssertionError):
                print ('Failed assertion to ensure merge file exists')
                raise
            except:
                print ('Unexpected Error')
                raise
            
            self.merge(file_a, file)
        
"""

# Test functions - not needed but retained for possible later testing
    
def buildnewtest():
    
    from shutil import copyfile
    from datetime import date,datetime
    
    
    filename1 = 'server.db'
    filename2 = 'sensor.db'

    # if we are root, write to root dir
    user = os.popen('echo $USER').read().strip()


    __RDIR__ = '/home/'+user
    
    file_a = os.path.join(__RDIR__,filename1)
    file_b = os.path.join(__RDIR__,filename2)
    
    if os.path.exists(file_a):
        os.remove(file_a)
    
    db_a = sqlite3.connect(file_a)
    db_a.execute('''
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
                     SP           REAL        NOT NULL,
                     RC           INT         NOT NULL,
                     NSAT         INT         
                     );
                 ''')
    db_a.execute('''
                 CREATE TABLE PUSH
                 (
                     SERIAL       CHAR(16)    NOT NULL,
                     TIME         CHAR(6)     NOT NULL,
                     DATE         CHAR(8)     NOT NULL
                     );
                 ''')


    db_a.commit()
    db_a.close()
    
    copyfile(os.path.join(__RDIR__,'Downloads',filename1),file_b)
    
    DATE = date.today().strftime("%d%m%Y")
    TIME = datetime.utcnow().strftime("%H%M%S")    
    
    db_b = sqlite3.connect(file_b)
    
    cursor_b = db_b.cursor()
    
    cursor_b.execute('SELECT SERIAL FROM MEASUREMENTS LIMIT 1')
    
    SERIAL = cursor_b.fetchall()[0][0]
    
    data = [(SERIAL,TIME,DATE,)]
    
    cursor_b.executemany("INSERT INTO PUSH (SERIAL,TIME,DATE) VALUES(?, ?, ?);", data )
    
    db_b.commit()
    db_b.close()
    
    return (file_a,file_b)

def main():

    (file_a,file_b) = buildnewtest()
    
    merge=sqlMerge()

    merge.merge(file_a, file_b)

    return

if __name__ == '__main__':
    main()
"""