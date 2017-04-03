#!/usr/bin/env python
from __future__ import print_function

import sys
import json
import requests

class FriskbySubmitter(object):
    """This class submits data from a database to the friskby cloud, then proceeds
    to mark the uploaded data as such.

    """

    def __init__(self, dao, config):
        self.device_config = config
        self.dao = dao

    def _upload(self, rows):
        if not rows:
            return
        print('Attempting to upload.')
        sys.stdout.flush()
        # id, value, sensor, timestamp, uploaded
        data = {}
        for row in rows:
            id_, value, sensor, timestamp, _ = row
            if sensor not in data:
                data[sensor] = []
            data[sensor].append((id_, value, sensor, timestamp))

        print('Connecting.')
        sys.stdout.flush()
        for sensor in data:
            sensor_id = self.device_config.getSensorId(sensor)
            push = {"sensorid"   : sensor_id,
                    "value_list" : [(x[3].isoformat(), x[1]) for x in data[sensor]], # (time, val)
                    "key"        : self.device_config.getPostKey()}
            print('Posting to %s' % self.device_config.getPostURL())
            print(push)
            sys.stdout.flush()
            respons = requests.post(self.device_config.getPostURL(),
                                    headers={'Content-Type': 'application/json'},
                                    data=json.dumps(push),
                                    timeout=30)
            print('posted %s' % sensor)
            sys.stdout.flush()
            if respons.status_code != 201:
                respons.raise_for_status()
                raise Exception('Server did not respond with 201 Created.  Response: %d %s'
                                % (respons.status_code, respons.text))
            respons.connection.close()
        return True # no exception, everything written

    def post(self):
        """Posts non-uploaded entries from the dao to the cloud.  Marks as
           uploaded in the dao if successfully uploaded."""
        if self.device_config is None:
            raise ValueError('Device config not set!')
        to_upload = self.dao.get_non_uploaded()
        print('Submitting ...')
        # TODO this is not particularly safe!
        # get_non_uploaded should at the very least be a context manager.
        sys.stdout.flush()
        if self._upload(to_upload):
            self.dao.mark_uploaded(to_upload)
