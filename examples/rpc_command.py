from keplerrpc import KeplerRPC
import sys

if len(sys.argv) != 3 and len(sys.argv) != 4:
  print("USAGE : {} <ttyUSB> <cmd> <args with , for multi args".format(sys.argv[0]))
  sys.exit(-1)

cli = KeplerRPC(sys.argv[1])
cmd = sys.argv[2]

if len(sys.argv) == 3:
  ret = cli.call(cmd)
  args = None
else:
  arglist = sys.argv[3].split(',')
  args = [float(k) if '.' in k else int(k) for k in arglist]
  ret = cli.call(cmd,*args)

print('cmd {} with args {} returned {}.'.format(sys.argv[2], args, ret))

