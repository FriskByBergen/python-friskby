from unittest import TestCase, skipUnless, skipIf
from friskby import MockSDS011

class SDS011Test(TestCase):

    def test_read_mock(self):
        pm10, pm25 = MockSDS011('/device/sds011').read()
        self.assertEqual(10.0, pm10)
        self.assertEqual(2.5, pm25)
