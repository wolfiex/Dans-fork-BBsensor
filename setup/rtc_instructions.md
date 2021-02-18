# Login
1. ssh into the pi
2. go to root `sudo -s`

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
date;
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


















# Install checks if misbehaving

### Remove default libraries (ONLY REQUIRED IF MISBEHAVING)
It seems that there now exists a library to do a lot of the manual heavy lifting. 
However we still need to make sure that the standard DS3231 driver is **NOT** loaded: 

#### ie. comment out in `/boot/config.txt`
```
dtoverlay=i2c-rtc,ds3231
```
only if it exists. If using a clone of my SD card, this has `#dtoverlay=i2c-rtc,pcf8523` instead which also needs to be commented out. 

