#!/bin/sh

LOCK=/tmp/lockfile_for_plug_usb

if [ -f $LOCK ]
then
        exit 1
else
        touch $LOCK
        # the actual command to run upon USB plug in
        /bin/date >> /root/usb.log
fi

