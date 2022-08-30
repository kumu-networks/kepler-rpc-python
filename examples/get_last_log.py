from keplerrpc import KeplerRPC
import sys

if len(sys.argv) != 2:
  print("USAGE : {} <ttyUSB>".format(sys.argv[0]))
  sys.exit(-1)

cli = KeplerRPC(sys.argv[1])

log = cli.call('get_last_log')

print(log)

