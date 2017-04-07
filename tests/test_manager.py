from __future__ import (absolute_import, print_function)

import json
from unittest import TestCase, main as unittest_main

from friskby import FriskbyManager


class FakePip():

    def __init__(self, code=None):
        self.code = code
        self.args = None

    def main(self, args=None):
        self.args = args
        return self.code


class FakeDeviceConfig():

    def __init__(self, config=dict()):
        self.config = config

    def downloadNew(self):
        return self

    def getChannel(self):
        return self.config["channel"]


class FriskbyManagerTest(TestCase):

    def test_sysinfo(self):
        sys_info = FriskbyManager.get_sys_info()
        self.assertTrue('sysname' in sys_info)
        self.assertTrue('requests' in sys_info)
        self.assertTrue('python' in sys_info)

        sys_info = FriskbyManager.get_sys_info()
        sys_info = json.dumps(sys_info, indent=4, sort_keys=True)
        print(sys_info)

    def test_nominal_and_stable_update(self):
        cfg = FakeDeviceConfig({"channel": "stable"})
        pip = FakePip(code=0)

        manager = FriskbyManager(cfg, pip=pip, managed_packages=["package1"])
        manager.update_client(cfg)

        self.assertEqual(pip.args, ["install", "--upgrade", "package1"])

    def test_failed_stable_update(self):
        cfg = FakeDeviceConfig({"channel": "stable"})
        pip = FakePip(code=255)

        manager = FriskbyManager(cfg, pip=pip, managed_packages=["package1"])

        with self.assertRaises(RuntimeError):
            manager.update_client(cfg)

    def test_nominal_lastes_update(self):
        cfg = FakeDeviceConfig({"channel": "latest"})
        pip = FakePip(code=0)

        manager = FriskbyManager(cfg, pip=pip, managed_packages=["package1"])
        manager.update_client(cfg)

        self.assertEqual(pip.args, ["install", "--upgrade", "--pre",
                                    "package1"])

    def test_update_when_no_channel_provided(self):
        cfg = FakeDeviceConfig()
        pip = FakePip(code=0)

        manager = FriskbyManager(cfg, pip=pip, managed_packages=["package1"])
        manager.update_client(cfg)

        self.assertEqual(pip.args, ["install", "--upgrade", "package1"])


if __name__ == '__main__':
    unittest_main()
