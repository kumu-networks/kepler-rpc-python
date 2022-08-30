from keplerrpc import KeplerRPC
import sys

import numpy as np

if len(sys.argv) != 2 and len(sys.argv) != 3:
  print("USAGE : {} <ttyUSB> <opt : cent_freq_hz>".format(sys.argv[0]))
  sys.exit(-1)

cli = KeplerRPC(sys.argv[1])

if len(sys.argv) == 3:
    cent_freq_hz = float(sys.argv[2])
    freq_set = cli.call('center_freq', cent_freq_hz)
else:
    freq_set = cli.call('center_freq')

print("CENTER_FREQ = {}Hz".format(freq_set))

