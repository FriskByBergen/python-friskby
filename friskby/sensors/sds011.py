#!/usr/bin/env python
from __future__ import division, print_function
from os.path import exists
import time
from serial import Serial, SerialException


class SDS011(object):
    """A class for reading PM10 and PM25 from the SDS011 sensor.'

    Takes as input the path to the device, e.g. 'dev/ttyUSB0' or
    '/dev/ttyAMA0'.  Has one method, read, which reads for

    """
    MSG_START = 170  # AAC0
    MSG_CMD = 192
    MSG_END = 171

    def __init__(self, device_path, sleep_time=0.01):
        self.sleep_time = sleep_time
        if not exists(device_path):
            raise IOError('[Errno 2] No such device %s' % device_path)
        self.device = Serial(device_path, baudrate=9600,
                             stopbits=1, parity="N", timeout=2)

    def _fastforward(self):
        """Reads from device until [MSG_START=AAC0, MSG_CMD] encountered"""
        while True:
            byte_read = self.device.read(1)
            if len(byte_read) < 1:
                raise SerialException('Device timed out in attempt to read a byte.')
            if ord(byte_read) == SDS011.MSG_START:
                byte_read = self.device.read(1)
                if ord(byte_read) == SDS011.MSG_CMD:
                    return
            time.sleep(self.sleep_time)

    def _read_values(self):
        """Reads 8 values as bytes and their int values"""
        bytes_read = self.device.read(8)
        if len(bytes_read) != 8:
            raise SerialException('Device timed out in attempt to read values.')
        return map(ord, bytes_read)

    def read(self):
        """Samples from sensor, verifies correctness and returns a pair
        of float values (pm10, pm25)."""
        self._fastforward()
        pm25hb, pm25lb, pm10hb, pm10lb, d5, d6, cs, tail = self._read_values()

        cs_expected = (pm25hb + pm25lb + pm10hb + pm10lb + d5 + d6) % 256
        if cs != cs_expected:
            raise Exception("Checksum test failed")

        if tail != SDS011.MSG_END:
            raise Exception("Message was not correctly terminated?")

        pm25 = float(pm25hb + pm25lb*256)/10.0
        pm10 = float(pm10hb + pm10lb*256)/10.0

        return (pm10, pm25)

if __name__ == '__main__':
    import sys
    PATH = '/dev/ttyUSB0'
    if len(sys.argv) == 2:
        PATH = sys.argv[1]

    SENSOR = None
    try:
        SENSOR = SDS011(PATH)
    except IOError as i_err:
        if '[Errno 13]' in str(i_err):
            sys.exit('[Errno 13] Permission denied for %s.  Try with sudo.' % PATH)
        if '[Errno 2]' in str(i_err):
            sys.exit('No such device %s. Try another path or port.' % PATH)
        sys.exit('Failed to connect to device at %s.\n%s' % (PATH, i_err))
    if not SENSOR:
        sys.exit('Failed to connect to %s.' % PATH)

    try:
        PM10PM25 = SENSOR.read()
        print('%.2f %.2f' % PM10PM25)
    except SerialException as s_err:
        sys.exit('Error during sampling: %s.' % s_err)
