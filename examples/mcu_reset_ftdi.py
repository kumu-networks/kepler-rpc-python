import time
from pyftdi import ftdi
import sys
ff = ftdi.Ftdi()
ff.open_from_url('ftdi://:/1')
ff.set_cbus_direction(0b0010, 0b0010)
if len(sys.argv) == 1:
  ff.set_cbus_gpio(0b0000)
  time.sleep(0.5)
  ff.set_cbus_gpio(0b0010)
else:
  val = int(sys.argv[1])
  if val == 0:
    ff.set_cbus_gpio(0b0000)
  elif val == 1:
    ff.set_cbus_gpio(0b0010)
  else:
    print("USAGE: val should be 0 of 1")
ff.close()

