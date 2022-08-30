from keplerrpc import KeplerRPC
import sys
import os
import time

if len(sys.argv) != 3:
  print("USAGE: {} </dev/ttyUSBx> <.bin>")

cli = KeplerRPC(sys.argv[1])

os.system('systemctl stop keplerserver')
cli.call('bootloader')
time.sleep(0.5)
os.system('stm32loader -b 57600 -p {} -e -w -v {} -g 0x08000000'.format(sys.argv[1], sys.argv[2]))
os.system('python3 ~/kepler-rpc-python/examples/mcu_reset.py')
print('Rebooting...')
time.sleep(10)
print('Reprogramming done!')

