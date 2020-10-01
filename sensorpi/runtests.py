import os
print('This is pi of serial number: ',os.popen('cat /sys/firmware/devicetree/base/serial-number').read())

import tests.gps_test


# import tests.pyvers
# import tests.interrupt_test
# import tests.opc_test
# import tests.db_test


# import tests.ctrlc_test
