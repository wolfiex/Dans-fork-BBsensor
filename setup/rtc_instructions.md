------
Warning, unplugging the RTC corrupts it. Solution, reboot the PI with internet to resync. 
------

# Login
1.  ssh into the pi
2.  Log in as root `sudo -s`

# Installation 

This has been added to the general install script in this repo. If this was not run the following manual setup code below can be run. 

# Run the following:
```
cd;
git clone https://github.com/bablokb/pi-wake-on-rtc.git;
cd pi-wake-on-rtc;
sudo tools/install;

```

# Check the time difference
## example code
```
# pi date
date;  

# rtc date
sudo rtcctl show date;
```
## Example output
```
root@bbsensor00:~/pi-wake-on-rtc# date
Thu 18 Feb 19:24:13 GMT 2021
root@bbsensor00:~/pi-wake-on-rtc# sudo rtcctl show date
date:   2000-01-01 00:09:52
```

# Sync RTC with onboard clock

## sync rtc

```
sudo rtcctl init
```
## Check the time as above
```
root@bbsensor00:~/pi-wake-on-rtc# sudo rtcctl show date
date:   2021-02-18 19:30:20
root@bbsensor00:~/pi-wake-on-rtc# date
Thu 18 Feb 19:30:24 GMT 2021
```

***********
stop here
**********




## TEST time from RTC
We start by breaking the system time configuration and setting the month and time to july 

```
sudo date -s "Jul 5 08:10"
```

## Time difference
Now unless we ran the above command at 8 am in July there will be a clock difference
```
root@bbsensor00:~/pi-wake-on-rtc# sudo rtcctl show
date:   2021-02-18 19:45:30
sys:    2021-07-05 08:14:26.029449
alarm1: 2021-07-18 20:30:18
        (enabled: False)
        (fired:   False)
alarm2: 2021-07-18 20:30:00
        (enabled: False)
        (fired:   False)
```

## truncate rtc time
```
sudo rtcctl show date | cut -c9- 
```

## Use this to set the rpi date
```
## set date from RTC
sudo date -s "$(sudo rtcctl show date | cut -c9- )"
```


# Setting alarm 
The plan is to clear the alarm on boot. We then read the date, and set another one for the next working day 


## Next working day 
```
## where last day is todays date
last_day=`date +%Y%m%d`
nwd=$(date -d "$last_day +$( if [ `date -d $last_day +%w` == 5 ]; then echo 3; elif [ `date -d $last_day +%w` == 6 ]; then echo 2; else echo 1; fi ) days" +"%d.%m.%Y")
echo $last_day $nwd
```

## setting an alarm

### Format
The format required is 
```
Format: dd.mm.YYYY [HH:MM[:SS]] or mm/dd.YYYY [HH:MM[:SS]]
```
### Set code
We use the above snippet to set an alarm for 7 am on the next working day
```
# set an alarm 7 am next working day
sudo rtcctl set alarm1 $(date -d "$last_day +$( if [ `date -d $last_day +%w` == 5 ]; then echo 3; elif [ `date -d $last_day +%w` == 6 ]; then echo 2; else echo 1; fi ) days" +"%d.%m.%Y 07:00") 
# dont forget to turn it on 
sudo rtcctl on alarm1
```

### Check alarm
```
sudo rtcctl show alarm1
```

### Clear alarm
``` 
sudo rtcctl clear alarm1
```




# Current state of RPI Sensors. 
Although the chips are able to produce alarms and wake calls, the units purchased do not have the relevant pin connected (labelled as NC - not connected). 

## Plan 

The plan is to have the RC code to run reset the alarm for the next working day. 

The sensor will then run normally. If the sensor is initated within a normal schoolday, then it will automatically shut down after 7 pm. It will then be woken up in the morning at 7 am as set. 


Should the sensor be turned on out of hours (development mode) it will not automatically shut down again, but remain on as usual. 


### Situation
The clock is currently only just run to adjust the system time. 









# Install checks if misbehaving

### Remove default libraries (ONLY REQUIRED IF MISBEHAVING)
It seems that there now exists a library to do a lot of the manual heavy lifting. 
However we still need to make sure that the standard DS3231 driver is **NOT** loaded: 

#### ie. comment out in `/boot/config.txt`
```
dtoverlay=i2c-rtc,ds3231
```
only if it exists. If using a clone of my SD card, this has `#dtoverlay=i2c-rtc,pcf8523` instead which also needs to be commented out. 

