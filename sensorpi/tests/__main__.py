''' 
python3 -m sensorpi.tests
'''

import os
print('This is pi of serial number: ',os.popen('cat /sys/firmware/devicetree/base/serial-number').read())




# from . import pyvers
# from . import interrupt_test
# from . import db_test
# 
from . import DHT_test
# from . import opc_test
from . import gps_test





# from . import tests.ctrlc_test
