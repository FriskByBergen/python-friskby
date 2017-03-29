import tempfile
from unittest import TestCase
from friskby import FriskbySubmitter, DeviceConfig

class FriskbySubmitterTest(TestCase):

    def setUp(self):
        _, self.cfg_fname = tempfile.mkstemp()
        _, self.sql_fname = tempfile.mkstemp()
        url_ = "https://friskby.herokuapp.com/sensor/api/device/FriskPITest/"
        deviceconfig = DeviceConfig.download(url_, post_key="xxx")
        deviceconfig.save(filename=self.cfg_fname)

    def test_friskby_submitter(self):
        subm = FriskbySubmitter(self.sql_fname, self.cfg_fname)
        subm.post() # empty post should be noop
