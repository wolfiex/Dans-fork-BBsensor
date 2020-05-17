sudo apt-get -y update;
sudo apt-get -y upgrade;

sudo apt-get install -y git python3-pip;
sudo apt-get install -y python-serial python3-serial;
sudo apt-get install -y python-dev python3-dev;
sudo apt-get install -y python-spidev python3-spidev;
sudo apt-get install -y python-smbus;
sudo apt-get install -y i2c-tools;
sudo apt-get install python3-ipython;



#/dev/ttyS0 is owned by the user root and the group dialout, so to be able to acesss the serial device, I would add myself to the dialout group:

sudo usermod -a -G tty $USER
sudo chmod 666 /dev/ttyS0

#sudo apt-get install bluez python-bluez;
