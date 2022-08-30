from keplerrpc import KeplerRPC
import keplerrpc
import sys
import os
import binascii
import time

cli = KeplerRPC(sys.argv[1])

loc = 0x2000
CHUNKSIZE = 2048

def send_partial(addr, data):
  dlen = len(data)
  for i in range(10):
    ret = dlen
    try:
      ret = cli.call('write_fpga_flash', addr, binascii.crc32(data), data)
    except keplerrpc.client.RPCError:
      print("retrying {} sending img addr {}".format(i+1, addr))
    else:
      break
    if ret != dlen:
      raise RuntimeError('write_fpga_flash addr {:x} len {} gave ret {}'.format(addr, dlen, ret))

with open(sys.argv[2], mode='rb') as f:
  imgbin = f.read()
  print("imagefile {}, size {} bytes @ addr {}".format(sys.argv[2], len(imgbin), hex(loc)))
  ll = len(imgbin).to_bytes(4, 'little')
  imgdata = ll+imgbin

  print("erase_fpga_flash size {} bytes @ addr {}".format(len(imgdata), hex(loc)))
  ret = cli.call('erase_fpga_flash',loc, len(imgdata))
  print("erase_fpga_flash completed, calling write_fpga_flash")

  timenow = time.time()
  offset = 0
  while offset + CHUNKSIZE <= len(imgdata):
    send_partial(loc+offset, imgdata[offset:offset+CHUNKSIZE])
    offset += CHUNKSIZE
    if (offset % (1024000/4) == 0):
      print("sending {} bytes... elapsed {} sec, estimated remaining time : {} sec".format(offset, time.time()-timenow, (time.time()-timenow)/offset*len(imgdata)-(time.time()-timenow)))

  send_partial(loc+offset, imgdata[offset:])
  lastlen = len(imgdata[offset:])
  offset += lastlen
  
print("sending FPGA image with {} bytes done".format(offset))

