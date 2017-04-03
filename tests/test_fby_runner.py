from __future__ import (absolute_import, print_function)
import os
import json
from unittest import TestCase
from random import randint

from friskby import FriskbyRunner, DeviceConfig


class FriskbyRunnerTest(TestCase):

    def setUp(self):
        _tmp_f = '/tmp/%d' % randint(2**30, 2**32)
        url_ = "https://friskby.herokuapp.com/sensor/api/device/FriskPITest/"
        deviceconfig = DeviceConfig.download(url_, post_key="xxx")
        deviceconfig.save(filename=_tmp_f)
        self.cfg = deviceconfig


    def test_load(self):
        _ = FriskbyRunner(self.cfg)

    def test_sysinfo(self):
        sys_info = FriskbyRunner.get_sys_info()
        self.assertTrue('sysname'  in sys_info)
        self.assertTrue('requests' in sys_info)
        self.assertTrue('python'   in sys_info)

        sys_info = FriskbyRunner.get_sys_info()
        sys_info = json.dumps(sys_info, indent=4, sort_keys=True)
        print(sys_info)
