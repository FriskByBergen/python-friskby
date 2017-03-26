#!/usr/bin/env python
from __future__ import (print_function, absolute_import)

import sys
import os
import json
from traceback import format_exception

from .friskby_dao import FriskbyDao
from .device_config import DeviceConfig
from .os_release import sys_info

class FriskbyRunner(object):

    def __init__(self, root=None, config_file=None, var_path=None):
        if not root:
            self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
        self.config_file = config_file
        if not config_file:
            self.config_file = os.path.join(self.root, "etc/config.json")
        if not var_path:
            var_path = os.path.join(self.root, "var")

        self._sample_time = 10 * 60
        self._sleep_time = 0.5
        self._accuracy = 4 # round observation to fourth digit
        self._config = None
        self._sql_path = os.path.join(var_path, 'friskby.sql')
        self._dao = FriskbyDao(self._sql_path)

    def install(self, config):
        # TODO should we do pip install --upgrade reuirements from config?
        config.save(filename=self.config_file)

    def update_client(self, config):
        new_config = config.downloadNew() # TODO what is this now?


    def _handle_post_exception(self, err, exc_info):
        err_msg = '(unknown error for %s)' % str(type(err))
        try:
            err_msg = str(err)
        except Exception:
            pass
        exc_type, exc_value, exc_tb = exc_info
        tb_list = format_exception(exc_type, exc_value, exc_tb)
        log_payload = 'Exception caught: "%s".' % (err_msg)
        traceback = "".join(tb_list)
        try:
            self._config.logMessage(log_payload, long_msg=traceback)
        except:
            sys.stderr.write('Error submitting log message!')

    def run(self):
        self._config = DeviceConfig(self.config_file)
        long_msg = self.get_sys_info()
        self._config.logMessage("Starting up", long_msg=long_msg)
        self._config.postVersion()

        try:
            self.update_client(self._config)
        except Exception as err:
            self._handle_post_exception(err, sys.exc_info())
            raise

    @classmethod
    def get_sys_info(cls):
        info = {}
        try:
            info = sys_info()
            if info:
                info = json.dumps(info, indent=4, sort_keys=True)
        except Exception as err:
            info = 'Error getting sys_info: "%s".' % err
        return info
