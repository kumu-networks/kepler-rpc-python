from keplerrpc import KeplerRPC
import sys
import msgpack

import numpy as np
import struct

import binascii

loc = 0x1000
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


if len(sys.argv) != 7:
  print("USAGE: {} </dev/ttyUSBx> <Kepler serialNo> <Maxwell serialNo> <Maxwell hwvariant> <dciq_caldata.csv> <box_caldata.csv>".format(sys.argv[0]))
  sys.exit(-1)
cli = KeplerRPC(sys.argv[1])
serialk = int(sys.argv[2])
serialm = int(sys.argv[3])
variantm = int(sys.argv[4])
cal_format = 1
kepler_hwver = 1
box_hwver = 1

with open(sys.argv[5],'r') as ff:
    header = ff.readline()[:-1].split(',')
    data = []
    ll = ff.readline()
    while ll:
        data.append(np.fromstring(ll[:-1], dtype=float, sep=','))
        ll = ff.readline()

print(header)

startfreq = data[0][header.index('cent_freq')]
stopfreq = data[-1][header.index('cent_freq')]
freqstep = data[1][header.index('cent_freq')] - data[0][header.index('cent_freq')]

print(startfreq,stopfreq,freqstep)

flashdata_kepler = struct.pack('<iBBHddd', 0x554d554b, cal_format, kepler_hwver, serialk, startfreq, stopfreq, freqstep)

for dd in data:
    dd = [int(x) for x in dd]
    caldata = struct.pack('<BBH', dd[header.index('dn0_dcoi')], dd[header.index('dn0_dcoq')], (dd[header.index('dn0_pherr')]*2**6)+dd[header.index('dn0_gerr')])
    caldata += struct.pack('<BBH', dd[header.index('dn1_dcoi')], dd[header.index('dn1_dcoq')], (dd[header.index('dn1_pherr')]*2**6)+dd[header.index('dn1_gerr')])
    caldata += struct.pack('<hhhhhh', dd[header.index('up0_dl_dcoi')], dd[header.index('up0_dl_dcoq')], dd[header.index('up0_ul_dcoi')], dd[header.index('up0_ul_dcoq')], dd[header.index('up0_iqwi')], dd[header.index('up0_iqwq')])
    caldata += struct.pack('<hhhhhh', dd[header.index('up1_dl_dcoi')], dd[header.index('up1_dl_dcoq')], dd[header.index('up1_ul_dcoi')], dd[header.index('up1_ul_dcoq')], dd[header.index('up1_iqwi')], dd[header.index('up1_iqwq')])
    flashdata_kepler += caldata

common = {}
with open(sys.argv[6],'r') as ff:
    rawll = ff.readline()[:-1]
    while rawll[0] == '%':
      aa = rawll[1:].replace(" ","").replace("="," ").split()
      common[aa[0]] = float(aa[1])
      rawll = ff.readline()[:-1]

    header = rawll.split(',')
    data = []
    ll = ff.readline()
    while ll:
        data.append(np.fromstring(ll[:-1], dtype=float, sep=','))
        ll = ff.readline()

startfreq = data[0][header.index('cent_freq')]
stopfreq = data[-1][header.index('cent_freq')]
freqstep = data[1][header.index('cent_freq')] - data[0][header.index('cent_freq')]

boxcal_format = 2

flashdata_box = struct.pack('<iBBBBffddd', 0x554d554b, boxcal_format, box_hwver, variantm, serialm, common['ref_dl_atten_db'], common['ref_ul_atten_db'], startfreq, stopfreq, freqstep)

for dd in data:
    dd = [float(x) for x in dd]
    caldata = struct.pack('<ffffffff', \
        dd[header.index('donor0rx_dbm_to_dbfs')], dd[header.index('donor1rx_dbm_to_dbfs')], dd[header.index('donor0tx_dbfs_to_dbm')], dd[header.index('donor1tx_dbfs_to_dbm')], \
        dd[header.index('server0rx_dbm_to_dbfs')], dd[header.index('server1rx_dbm_to_dbfs')], dd[header.index('server0tx_dbfs_to_dbm')], dd[header.index('server1tx_dbfs_to_dbm')])
    flashdata_box += caldata


ret = cli.call('erase_fpga_flash',loc, len(flashdata_kepler) + len(flashdata_box))
print("erase_fpga_flash of size {} completed, calling write_fpga_flash".format(len(flashdata_kepler)+len(flashdata_box)))


offset = 0
while offset + CHUNKSIZE <= len(flashdata_kepler):
  send_partial(loc+offset, flashdata_kepler[offset:offset+CHUNKSIZE])
  offset += CHUNKSIZE

send_partial(loc+offset, flashdata_kepler[offset:])
lastlen = len(flashdata_kepler[offset:])
offset += lastlen
  
print("writing Kepler cal data with {} bytes done".format(offset))

loc = 0x1800
CHUNKSIZE = 2048

offset = 0
while offset + CHUNKSIZE <= len(flashdata_box):
  send_partial(loc+offset, flashdata_box[offset:offset+CHUNKSIZE])
  offset += CHUNKSIZE

send_partial(loc+offset, flashdata_box[offset:])
lastlen = len(flashdata_box[offset:])
offset += lastlen
  
print("writing box cal data with {} bytes done".format(offset))

