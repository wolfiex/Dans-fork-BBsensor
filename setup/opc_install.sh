git submodule update --init --recursive;
pip3 install pyusbiss;
pip install git+https://github.com/doceme/py-spidev.git;

cd py-opc-R1 && sudo python3 setup.py develop ; cd -

