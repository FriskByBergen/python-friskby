from __future__ import division

import time
import serial


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
        self.device = serial.Serial(device_path, baudrate=9600,
                                    stopbits=1, parity="N", timeout=2)

    def _fastforward(self):
        """Reads from device until [MSG_START=AAC0, MSG_CMD] encountered"""
        while True:
            byte_read = self.device.read(1)
            if len(byte_read) < 1:
                raise IOError('Device timed out in attempt to read a byte.')
            if ord(byte_read) == SDS011.MSG_START:
                byte_read = self.device.read(1)
                if ord(byte_read) == SDS011.MSG_CMD:
                    return
            time.sleep(self.sleep_time)

    def _read_values(self):
        """Reads 8 values as bytes and their int values"""
        bytes_read = self.device.read(8)
        if len(bytes_read) != 8:
            raise IOError('Device timed out in attempt to read values.')
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
