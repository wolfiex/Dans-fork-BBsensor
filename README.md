# BBServer!
OPC R1 server scripts for Pi3


## Setup
### seting up logger
`bash setup/opc_install.sh`

#### Then run the relevant tests
`cd serverpi && python3 runtests.py`

### server
`bash setup/...install.sh`


## link .rc_local to the mainbashrc 
Open `sudo nano /etc/rc.local`
and source the local rc file in this directory. 

For testing this will likely be under `/home/pi/BBSensor/rc.local` but will eventually NEED to be changed to the `/root` folder when deployed permanently. 

We add the lines:

``` source activate sudo nano /etc/rc.local ```

### rc.local contents

This contains:
- network clock updates
- code to run measurement unit on boot
- server init


