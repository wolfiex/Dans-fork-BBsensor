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



















# Install checks if misbehaving

### Remove default libraries (ONLY REQUIRED IF MISBEHAVING)
It seems that there now exists a library to do a lot of the manual heavy lifting. 
However we still need to make sure that the standard DS3231 driver is **NOT** loaded: 

#### ie. comment out in `/boot/config.txt`
```
dtoverlay=i2c-rtc,ds3231
```
only if it exists. If using a clone of my SD card, this has `#dtoverlay=i2c-rtc,pcf8523` instead which also needs to be commented out. 

