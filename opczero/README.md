## To Do
- [x] Threading to read last GPS entry and read the sensor for syncronous result generation
- [ ] power down usb when not in use
- [x] test/boot and run scripts
- [x] automatic reconnecting of GPS usb when disconnected (update port)
- [x] power LED inidicatior
- [x] remove 'wait for network on boot'
- [ ] on wifi, upload (limited to once every two hours (param) ), move data to archive folder
- [x] datafile location based on user (home/root) - update to use HOME env var at later point
- [ ] reenable reboot on fail
- [ ] log location on boot updata

## Reading Materials     
### How GPS works - the Compendium_Book
https://www.u-blox.com/sites/default/files/products/documents/GPS-Compendium_Book_%28GPS-X-02007%29.pdf


## Test
`python3 -m gps`

## Threading
The main program structure polls both the GPS and particulate counter on the device in separate functions using the python threading library. 

For a raspberry Pi, each of these are done on a separate core. The Pi zero however is a single core device. This means that the work can still be done in separate threads, however that the performance gain (if any) will not be the same. Threading however does aid in the partitioning of different tasks within the program and shall still be used. 


