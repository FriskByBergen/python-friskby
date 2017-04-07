#!/usr/bin/env python
from __future__ import (print_function, absolute_import)

import json
import sys

from .os_release import sys_info
from time import sleep


SYSTEMD_NAME = 'org.freedesktop.systemd1'
SYSTEMD_OBJ = '/org/freedesktop/systemd1'
SYSTEMD_UNIT_IFACE = 'org.freedesktop.systemd1.Unit'
DBUS_PROPERTIES_IFACE = 'org.freedesktop.DBus.Properties'
SYSTEMD_MANAGER_IFACE = 'org.freedesktop.systemd1.Manager'


class FriskbyManager(object):

    def __init__(self, device_config, dbus=None, pip=None,
                 managed_packages=None, managed_services=None):
        """Creates a Friskby manager. Given a config, the manager will upgrade
        the client's pip packages, and appropriately reload/restart any systemd
        units it manages.

        managed_packages is a list of pip packages that it will upgrade
            (according to the config's channel value).
        managed_services is a list of systemd services.
        """
        self._config = device_config
        self._dbus = dbus
        self._pip = pip
        self._managed_packages = managed_packages
        self._managed_services = managed_services

    def __run_post_install(self):
        """
        Checks if any known service needs a daemon-reload. If a service needs
        it, we do a daemon-reload, wait, then restart each service.
        """
        if self._dbus is None:
            print("No DBus provided, post-install can't run.")
            sys.stdout.flush()
            return

        if len(self._managed_services) == 0:
            print("No services to manage.")
            sys.stdout.flush()
            return

        sysbus = self._dbus.SystemBus()
        systemd1_obj = sysbus.get_object(SYSTEMD_NAME, SYSTEMD_OBJ)
        manager = self._dbus.Interface(systemd1_obj, SYSTEMD_MANAGER_IFACE)

        restart_units = []
        for unit in self._managed_services:
            unit_obj_path = manager.GetUnit(unit)
            unit_obj = sysbus.get_object(SYSTEMD_NAME, unit_obj_path)
            unit_proxy = self._dbus.Interface(unit_obj, SYSTEMD_UNIT_IFACE)
            props_proxy = self._dbus.Interface(unit_obj, DBUS_PROPERTIES_IFACE)
            need_reload = props_proxy.Get(SYSTEMD_UNIT_IFACE,
                                          'NeedDaemonReload')
            if need_reload:
                restart_units.append(unit_proxy)
                print("Unit %s required daemon-reload." % unit)
                sys.stdout.flush()

        # TODO: instead of sleeping, we could track the job and wait for it
        # to finish.
        if len(restart_units) > 0:
            manager.Reload()
            sleep(5)

        for u in restart_units:
            u.Restart('replace')

    def install(self, config):
        # TODO should we do pip install --upgrade reuirements from config?
        config.save()

    def update_client(self, config):
        """Updates or upgrades the client's pip packages.

        Raises RuntimeError should pip return a non-zero exit code.
        """
        if self._pip is None:
            print("No pip provided, post install can't run.")
            sys.stdout.flush()
            return

        if len(self._managed_packages) == 0:
            print("No packages to manage.")
            sys.stdout.flush()
            return

        new_config = config.downloadNew()

        channel = 'stable'
        try:
            channel = new_config.getChannel()
        except KeyError:
            pass  # No channel defined, use stable.

        args = ["install", "--upgrade"]
        if channel == 'latest':
            args.append("--pre")
        args = args + self._managed_packages

        ret = self._pip.main(args=args)
        if ret == 0:
            self.__run_post_install()
        else:
            raise RuntimeError("Pip exited with non-zero code: %d" % ret)

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
