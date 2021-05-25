sudo apt-get -y update;
sudo apt-get -y upgrade;

sudo apt-get install -y python-dev python-rpi.gpio ;
sudo apt-get install -y git python3-pip;
sudo apt-get install -y python-serial python3-serial;
# sudo apt-get install -y python-dev python3-dev;
# sudo apt-get install -y python-spidev python3-spidev;
sudo apt-get install -y python-smbus;
sudo apt-get install -y i2c-tools;
sudo apt-get install -y python3-ipython;
sudo apt-get install -y screen;

git submodule update --init --recursive;
pip3 install pyusbiss;
pip3 install git+https://github.com/doceme/py-spidev.git;

cd py-opc-R1 && sudo python3 setup.py develop ; cd -

pip3 install db-sqlite3;
pip3 install cryptography;

pip3 install wifindme;
sudo apt-get install ntp --yes ;
sudo timedatectl set-ntp true
pip3 install Adafruit_DHT;
pip3 uninstall numpy -y;
sudo apt-get install python3-numpy --yes ;
pip3 install pandas;

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

#/dev/ttyS0 is owned by the user root and the group dialout, so to be able to acesss the serial device, I would add myself to the dialout group:

sudo usermod -a -G tty $USER ;
sudo chmod 666 /dev/ttyS0 ;

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


mv /root/se*r.db pre_setupscript_sr.db;
if [[ ! -f /root/server.db && ! -f /root/sensor.db ]]; then
  cd /root/BBSensor && python3 -m sensorpi.SensorMod.db new;
fi
cd /root/BBSensor && python3 -m sensorpi.tests;

echo "$BB_VERSION" > /root/.params
echo `xxd -p -r <(echo "$SP_UNAME")` >> /root/.params
echo `xxd -p -r <(echo "$SP_PASSWORD")` >> /root/.params

sudo reboot;
