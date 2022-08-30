from serial import Serial
from msgpack import Packer, Unpacker
import time

class KeplerRPC:

    def __init__(self, devpath, baudrate=345600):
#    def __init__(self, devpath, baudrate=115200):
        self._devpath = devpath
        self._baudrate = baudrate
        self._dev = None
        self._msg_id = 0
        self._packer = Packer(use_bin_type=True)
        """
        For backwards compatibility, try these kwargs in order, until one succeeds.
        * 'encoding' and 'unicode_errors' options are deprecated. There is new 'raw' option.
          It is True by default for backward compatibility, but it is changed to False in
          near future. You can use raw=False instead of encoding='utf-8'.
        * For backwards compatibility, set 'max_buffer_size' explicitly.
        * For backwards compatibility, set 'strict_map_key' to False explicitly, when possible.
        """
        kwargs_list = (
            {'strict_map_key': False, 'raw': False},
            {'raw': False},
            {'encoding': 'utf-8'},
        )
        for kwargs in kwargs_list:
            try:
                self._unpacker = Unpacker(
                    use_list=True, max_buffer_size=2**31-1, **kwargs)
            except TypeError as ex:
                continue
            break
        else:
            raise RuntimeError('Failed to create unpacker.')
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        if self._dev is not None:
            raise RuntimeError('Device has already been opened.')
        self._dev = Serial(port=self._devpath, baudrate=self._baudrate,
                           timeout=0)

    def close(self):
        if self._dev is not None:
            self._dev.close()
            self._dev = None

    SOF = b'\x3a\x77\x49\xc8'
    VERSION = 1

    def _receive(self):
        while True:
            chunk = self._dev.read(size=1048576)
            self._unpacker.feed(chunk)
            for response in self._unpacker:
                return response

    def _find_frame(self):
        header = b'\x00\x00\x00\x00'
        while True:
            word = self._dev.read(size=1)
            if not word:
                continue
            header = header[1:] + word
            if header == b'\x3a\x77\x49\xc8':
                break

    def call(self, method, *args):
        if not isinstance(method, str):
            raise TypeError('method: Expected str.')
        self._msg_id += 1
        request = [KeplerRPC.VERSION, self._msg_id, method, args]
        wdata = KeplerRPC.SOF + self._packer.pack(request)
        self._dev.write(wdata)
        self._find_frame()
        msg_id, ret_code, value = self._receive()
        if ret_code:
            raise RPCError('Non-zero return code: {}'.format(ret_code))
        elif self._msg_id != msg_id:
            raise RPCError('Message ID mismatch: got = {}, expected = {}.'
                .format(msg_id, self._msg_id))
        return value

class RPCError(Exception):
    pass
