from tempfile import NamedTemporaryFile as temp
from unittest import TestCase
from friskby import FriskbySubmitter, DeviceConfig

class FriskbySubmitterTest(TestCase):

    def _temp_fname(self, postfix=''):
        tmpf = temp(delete=False)
        fname = tmpf.name + postfix
        tmpf.close()
        return fname

    def setUp(self):
        self.sql_fname = self._temp_fname('_db.sql')
        self.cfg_fname = self._temp_fname('_.cfg')
        url_ = "https://friskby.herokuapp.com/sensor/api/device/FriskPITest/"
        deviceconfig = DeviceConfig.download(url_, post_key="xxx")
        deviceconfig.save(filename=self.cfg_fname)

    def test_friskby_submitter(self):
        subm = FriskbySubmitter(self.sql_fname, self.cfg_fname)
        subm.post() # empty post should be noop
