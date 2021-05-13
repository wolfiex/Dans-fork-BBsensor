#Package updates

#For Staging Data - Sensors
pip3 install pysftp;

#For Uploading Data - ServerPi
pip3 install Office365-REST-Python-Client==2.2.2; # for uploading data to sharepoint
pip3 install adal;
pip3 install urllib3==1.24;
pip3 install boto3==1.9; # for uploading data to aws

#sudo pip3 install adafruit-circuitpython-ssd1306
sudo pip3 install adafruit-circuitpython-lis3dh
sudo apt install libopenjp2-7 libopenjp2-7-dev libopenjp2-tools --yes
pip3 install pillow
pip3 install adafruit-extended-bus

## RTC INSTALL
cd;
git clone https://github.com/bablokb/pi-wake-on-rtc.git;
cd pi-wake-on-rtc;
sudo tools/install;

date
sudo rtcctl show date

## sync rtc
sudo rtcctl init

date
sudo rtcctl show date

sudo apt autoremove -y;
echo 'finished'

#mv /root/se*r.db pre_setupscript_sr.db; # Enable if changes made to db structure
if [[ ! -f /root/server.db && ! -f /root/sensor.db ]]; then
  cd /root/BBSensor && python3 -m sensorpi.SensorMod.db new;
fi

echo "$BB_VERSION" > /root/.params
echo `xxd -p -r <(echo "$SP_UNAME")` >> /root/.params
echo `xxd -p -r <(echo "$SP_PASSWORD")` >> /root/.params

sudo reboot;
