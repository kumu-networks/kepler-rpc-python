import sys
from flask import Flask, render_template, request, Response, jsonify
from waitress import serve
import msgpack
import msgpack_numpy
import shlex

msgpack_numpy.patch()


import numpy as np
from keplerrpc import KeplerRPC

class Kepler():

  def __init__(self, port="/dev/ttyUSB1"):
    self._port = port
    self.cli = KeplerRPC(port)

  def call(self, method, *args):
    print("Kepler: call {} args {}".format(method, args))
    ret = self.cli.call(method, *args)
    return ret

  def load_pilot(self, waveform):
    ret = self.cli.call('pilot_enable',0)
    dd = (waveform.real.astype(dtype='int16') + (waveform.imag.astype(dtype='int16')*2**16))
    dd_b = dd.tobytes()
    ret = self.cli.call('load_pilot',dd_b)
    print("load_pilot : loaded {} samples : ret {}".format(len(dd_b), ret))

    self.cli.call('pilot_enable',1)
    return ret

  def tuner_test_load(self, tdd, tunerdata):
    dd_b = tunerdata.tobytes()
    print('tuner_test_load : tdd {} tunerdata len {} dd_b {} bytes'.format(tdd, len(tunerdata), len(dd_b)))
    ret = self.cli.call('tuner_test_load',tdd,dd_b)
    return ret
    
  def tuner_test_get(self, tdd):
    data = self.cli.call('tuner_test_get',tdd)
    arr = np.frombuffer(data, dtype='float32')
    return arr

  def canxfir_load(self, tdd, data):
    dd_b = data.tobytes()
    print('canxfir_load : tdd {} data len {} dd_b {} bytes'.format(tdd, len(data), len(dd_b)))
    ret = self.cli.call('canxfir_load',tdd,dd_b)
    return ret
    
  def canxfir_get(self, tdd):
    data = self.cli.call('canxfir_get',tdd)
    arr = np.frombuffer(data, dtype='float32')
    return arr
    
  def program_mcu(self, binfile):
    self.cli.call_noreply('bootloader')
    time.sleep(0.5)
    os.system('stm32loader -b 57600 -p {} -e -w -v {}'.format(self._port, binfile))
    time.sleep(0.5)
    os.system('stm32loader -p {} -g 0x08000000'.format(self._port))
    return '1'

  def reset_mcu(self):
    self.cli.call_noreply('bootloader')
    time.sleep(0.5)
    os.system('stm32loader -p {} -g 0x08000000'.format(self._port))
    return '1'

  def get_capture(self, group, length, triggered):
    data = self.cli.call('read_capture', group, length, triggered)
    arr = np.frombuffer(data, dtype='int16')
    ret = arr[0::2] + 1j*arr[1::2]
    return ret

app = Flask(__name__)


@app.route('/api/kepler/load_pilot', methods=['POST'])
def kepler_load_pilot():
    data = request.get_data()
    print('load_pilot: received {} bytes'.format(len(data)))
    obj = msgpack.unpackb(data, use_list=True, raw=False)
    tx_wfm = obj.astype('complex64')
    ret = _kepler.load_pilot(tx_wfm)
    return Response(str(ret), mimetype='text/html')

@app.route('/api/kepler/tuner_test_load,<tddstr>', methods=['POST'])
def kepler_tuner_test_load(tddstr):
    tdd = int(tddstr)
    print('tuner_test_load, tdd {}'.format(tdd))
    data = request.get_data()
    obj = msgpack.unpackb(data, use_list=True, raw=False)
    tunerdata = obj.astype('float32')
    ret = _kepler.tuner_test_load(tdd, tunerdata)
    return Response(str(ret), mimetype='text/html')

@app.route('/api/kepler/canxfir_load,<tddstr>', methods=['POST'])
def kepler_canxfir_load(tddstr):
    tdd = int(tddstr)
    print('canxfir_load, tdd {}'.format(tdd))
    data = request.get_data()
    obj = msgpack.unpackb(data, use_list=True, raw=False)
    tunerdata = obj.astype('float32')

    ret = _kepler.canxfir_load(tdd, tunerdata)
    return Response(str(ret), mimetype='text/html')

@app.route('/api/kepler/<command>')
def kepler_dispatch(command):
    command = command.lower().strip().lstrip(':')
    print("kepler_dispatch : " + command)

    if command.startswith('get_capture,'):
        group = int(command.split(',')[-3])
        length = int(command.split(',')[-2])
        triggered = int(command.split(',')[-1])
        print('got capture group {} len {} triggered {}'.format(group, length, triggered))
        capture = _kepler.get_capture(group, length, triggered)
        return Response(msgpack.packb(capture, use_bin_type=True), mimetype='application/x-msgpack')
    elif command.startswith('program_mcu'):
        filename = command.split(',')[-1]
        ret = _kepler.program_mcu(filename)
        return Response(str(ret), mimetype='text/html')
    elif command == 'reset_mcu':
        ret = _kepler.reset_mcu()
        return Response(str(ret), mimetype='text/html')
    elif command.startswith('tuner_test_get'):
        tdd = int(command.split(',')[-1])
        data = _kepler.tuner_test_get(tdd)
        return Response(msgpack.packb(data, use_bin_type=True), mimetype='application/x-msgpack')
    elif command.startswith('canxfir_get'):
        tdd = int(command.split(',')[-1])
        data = _kepler.canxfir_get(tdd)
        return Response(msgpack.packb(data, use_bin_type=True), mimetype='application/x-msgpack')
    else:
        aa = shlex.shlex(command)
        aa.whitespace += ','
        aa.whitespace_split = True
        cmd_list = list(aa)
        method = cmd_list[0]
        arglist = cmd_list[1:]
        args = [k[1:-1] if '"' in k else (float(k) if '.' in k else int(k)) for k in arglist]
        ret = _kepler.call(method, *args)
        return Response(str(ret), mimetype='text/html')

if len(sys.argv) != 3:
  print("USAGE: {} </dev/ttyUSBx> <server port number>")
  sys.exit(-1)

_kepler = Kepler(port=sys.argv[1])

app.config['PROPAGATE_EXCEPTIONS'] = True
print("Listening on port {}...".format(int(sys.argv[2])))
serve(app, host='0.0.0.0', port=int(sys.argv[2]))

