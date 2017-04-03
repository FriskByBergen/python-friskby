from tempfile import NamedTemporaryFile as temp
from unittest import TestCase
from friskby import FriskbyDao, FriskbySubmitter, DeviceConfig

class FriskbySubmitterTest(TestCase):

    def _temp_fname(self, postfix=''):
        tmpf = temp(delete=False)
        fname = tmpf.name + postfix
        tmpf.close()
        return fname

    def setUp(self):
        self.dao = FriskbyDao(self._temp_fname('_db.sql'))
        cfg_fname = self._temp_fname('_.cfg')
        url_ = "https://friskby.herokuapp.com/sensor/api/device/FriskPITest/"
        deviceconfig = DeviceConfig.download(url_, post_key="xxx")
        deviceconfig.save(filename=cfg_fname)
        self.cfg = deviceconfig

    def test_friskby_submitter(self):
        subm = FriskbySubmitter(self.dao, self.cfg)
        subm.post() # empty post should be noop
