import pandas as pd
from numpy import arctan2,random,sin,cos,degrees,nan
import os,sys,time
import matplotlib.pyplot as plt
from datetime import datetime



def parse(NAME):

    v=[]
    for i in tuple(open(NAME,'r')):
        i = i.strip('\x00') # rm empty bytes
        if i:# # skip blank lines
            v.append(eval('{%s}'%i.strip('/n')))



    df = pd.DataFrame(v[1:])
    full= len(df)
    df = df[df.gpstime!='']
    print('---- GPS connect %:',1- len(df)/(float(full)) ,full-len(df), 'values' )
    fulllat= len(df)
    df = df[df.lat!='']
    print('---- No gps coo %:',1- len(df)/(float(fulllat)) ,fulllat-len(df), 'values' )

    #df.utc = [i.split()[0] for i in df.utc]

    df['datetime']=[datetime.strptime(str(i),'%H%M%S.%f %Y-%m-%d') for i  in df.gpstime +' 2020-05-20']#+ df.utc ]     

    df.sort_values('datetime',inplace=True)

    df.set_index('datetime',inplace=True)

    df = df['lat lon PM1 PM2.5 PM10'.split()]


    def norm (x):
        return (x-min(x))/(max(x)-min(x))



    def convert_to_degrees(raw_value):
        decimal_value = raw_value/100.00
        degrees = int(decimal_value)
        mm_mmmm = (decimal_value - int(decimal_value))/0.6
        position = degrees + mm_mmmm
        #position = "%.4f" %(position)
        return position



    for i in 'lat lon'.split():
        df[i] = [convert_to_degrees(float(j)) for j in df[i]]


    df = df.astype(float)
    df['lon'] = -1*df['lon'] 

    return df
# df.to_csv('sensordata.csv')