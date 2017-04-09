from __future__ import absolute_import
import os.path
from sys import stderr

import json
import datetime
import tempfile
from urlparse import urlparse
import requests
import friskby

class DeviceConfig(object):
    required_keys = ["post_key", "sensor_list", "post_path", "config_path",
                     "server_url", "device_id"]

    def __init__(self, filename, post_key=None):
        if not os.path.isfile(filename):
            raise IOError("No such file: %s" % filename)

        config = None
        with open(filename, 'r') as js:
            config = json.load(js)
        if not "post_key" in config:
            if not post_key is None:
                config["post_key"] = post_key

        for key in self.required_keys:
            if not key in config:
                raise KeyError("Missing key:%s" % key)

        self.sha = None
        self.filename = filename
        self.data = config
        self.config_ts = datetime.datetime.now()

    def get_version(self):
        return friskby.VERSION

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return not self == other

    def save(self, filename=None):
        if filename is None:
            filename = self.filename

        path = os.path.dirname(filename)
        if not os.path.isdir(path):
            os.makedirs(path)

        with open(filename, "w") as fileH:
            fileH.write(json.dumps(self.data))

    def getServerURL(self):
        return self.data["server_url"]

    def getSensorId(self, sensor_type):
        vals = self.data['sensor_list']
        for s_id in vals:
            if sensor_type in s_id:
                return s_id
        return None

    def getConfigPath(self):
        return self.data["config_path"]

    def getPostURL(self):
        return "%s/%s" % (self.data["server_url"], self.data["post_path"])

    def getDeviceID(self):
        return self.data["device_id"]

    def getPostKey(self):
        return self.data["post_key"]

    def getChannel(self):
        return self.data["channel"]

    def updateRequired(self, new_config):
        return True  # TODO add logic

    def downloadNew(self):
        self.config_ts = datetime.datetime.now()
        update_url = "%s/%s" % (self.getServerURL(), self.getConfigPath())
        new_config = self.download(update_url, post_key=self.getPostKey())
        return new_config


    @classmethod
    def download(cls, url, post_key=None):
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise ValueError("http GET return status:%s" % response.status_code)

        _, config_file = tempfile.mkstemp()
        data = json.loads(response.content)
        tmp = urlparse(url)
        config = data["client_config"]
        config["server_url"] = "%s://%s" % (tmp.scheme, tmp.netloc)
        with open(config_file, "w") as f:
            f.write(json.dumps(config))

        config = DeviceConfig(config_file, post_key=post_key)
        os.unlink(config_file)
        config.filename = None

        return config

    def logMessage(self, msg, long_msg=None):
        data = {"key"     : self.getPostKey(),
                "device_id" : self.getDeviceID(),
                "msg" : msg}
        if long_msg:
            data["long_msg"] = long_msg
        json_msg = json.dumps(data, sort_keys=True)

        stderr.write('DeviceConfig.logMessage: %s\n' % json_msg)

        headers = {"Content-Type": "application/json"}
        response = requests.post("%s/sensor/api/client_log/" % self.getServerURL(),
                                 data=json_msg,
                                 headers=headers, timeout=10)
        return response.status_code

    def postVersion(self):
        data = {"key"     : self.getPostKey(),
                "git_ref" : "%s" % self.get_version()}
        headers = {"Content-Type": "application/json"}

        requests.put("%s/sensor/api/device/%s/" %
                     (self.getServerURL(), self.getDeviceID()),
                     data=json.dumps(data),
                     headers=headers,
                     timeout=10)

    def __repr__(self):
        content = '{}'
        try:
            content = json.dumps(self.data)
        except ValueError:
            pass
        return 'DeviceConfig(%s)' % content
