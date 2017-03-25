#!/usr/bin/env python
from __future__ import (print_function, absolute_import)

import sys
import os
import json
from traceback import format_exception

import friskby
from .friskby_dao import FriskbyDao
from .device_config import DeviceConfig
from .git_module import GitModule
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

    def get_dao(self):
        return self._dao

    def install(self, config):
        git_module = GitModule(url=config.getRepoURL())
        git_module.checkout(config.getGitRef())
        git_module.runTests("tests/run_tests")
        git_module.install(self.root,
                           files=None,
                           directories=None) # TODO
        config.save(filename=self.config_file)


    def rollback(self, config):
        self.install(config)


    def restart(self, config):
        self.install(config)
        os.execl(__file__, __file__)

        raise Exception("Fatal error: os.execl() returned - trying to rollback")

    def update_client(self, config):
        new_config = config.downloadNew()
        if config.updateRequired(new_config):
            try:
                config.logMessage("Restarting client - new version:%s" % new_config.getGitRef())
                self.restart(new_config)
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb_list = format_exception(exc_type, exc_value, exc_tb)
                config.logMessage("Restart failed - trying rollback", long_msg="".join(tb_list))
                self.rollback(config)
                config.logMessage("Rollback complete")


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
        self._config.postGitVersion()

        try:
            self.update_client(self._config)
        except Exception as err:
            self._handle_post_exception(err, sys.exc_info())
            raise

    @classmethod
    def get_sys_info(cls):
        info = ''
        try:
            info = sys_info()
            if info:
                info = json.dumps(info, indent=4, sort_keys=True)
        except Exception as err:
            info = 'Error getting sys_info: "%s".' % err
        return info
