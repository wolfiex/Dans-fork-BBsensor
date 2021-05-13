#Package updates
sudo apt-get update;

#For Staging Data - Sensors
pip3 install pysftp;

#For Uploading Data - ServerPi
pip3 install Office365-REST-Python-Client==2.2.2; # for uploading data to sharepoint
pip3 install adal;
pip3 install urllib3==1.24;
pip3 install boto3==1.9; # for uploading data to aws

#mv /root/se*r.db pre_setupscript_sr.db; # Enable if changes made to db structure
if [[ ! -f /root/server.db && ! -f /root/sensor.db ]]; then
  cd /root/BBSensor && python3 -m sensorpi.SensorMod.db new;
fi

echo "$BB_VERSION" > /root/.params
echo `xxd -p -r <(echo "$SP_UNAME")` >> /root/.params
echo `xxd -p -r <(echo "$SP_PASSWORD")` >> /root/.params

sudo reboot;
