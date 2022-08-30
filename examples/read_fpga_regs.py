from keplerrpc import KeplerRPC
import sys

import numpy as np

if len(sys.argv) != 4 and len(sys.argv) != 3:
  print("USAGE : {} <ttyUSB> <addr hex> <val hex(optional)>".format(sys.argv[0]))
  sys.exit(-1)

cli = KeplerRPC(sys.argv[1])

addr = int(sys.argv[2],16)

if len(sys.argv) == 4:
  val = int(sys.argv[3],16)
  data = cli.call('fpga_regs', addr, val)
  print("FPGA_REGS WRITE addr {} val 0x{:04x} ret 0x{:04x}".format(hex(addr), (0xffffffff & val), (0xffffffff & data)))
else:
  data = cli.call('fpga_regs', addr)
  print("FPGA_REGS READ addr {} ret 0x{:04x}".format(hex(addr), (0xffffffff & data)))



