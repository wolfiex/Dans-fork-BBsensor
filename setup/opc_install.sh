git submodule update --init --recursive;
pip3 install pyusbiss;
pip3 install git+https://github.com/doceme/py-spidev.git;

cd py-opc-R1 && sudo python3 setup.py develop ; cd -

pip3 install db-sqlite3
pip3 install cryptography

pip3 install wifindme
