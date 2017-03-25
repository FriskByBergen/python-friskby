from unittest import TestCase
from friskby import *

class FriskbyTest(TestCase):

    def test_friskby_import_all(self):
        # testing that TS and sys_info is imported on *
        t = TS()
        self.assertEqual([], t.data)
        self.assertTrue(len(sys_info()) > 0)
