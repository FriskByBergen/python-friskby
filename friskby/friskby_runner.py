#!/usr/bin/env python
from __future__ import (print_function, absolute_import)

import sys
import os
import json
from traceback import format_exception

from .os_release import sys_info

class FriskbyRunner(object):

    def __init__(self, device_config):
        self._config = device_config

    def install(self, config):
        # TODO should we do pip install --upgrade reuirements from config?
        config.save()

    def update_client(self, config):
        return config.downloadNew() # TODO what is this now?

    def run(self):
        # TODO this logic must be rewritten
        long_msg = self.get_sys_info()
        self._config.logMessage("Starting up", long_msg=long_msg)
        self._config.postVersion()

        self.update_client(self._config)


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
