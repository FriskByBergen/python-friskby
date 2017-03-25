from os import listdir
from os.path import isfile, join
import sys
from unittest import TestCase, skipUnless
import subprocess

try:
    subprocess.call(["pylint", "--version"])
    HAVE_PYLINT = True
except OSError:
    msg = '** Warning: Could not find pylint. Static checks skipped'
    sys.stderr.write(msg)
    HAVE_PYLINT = False

class PylintTest(TestCase):

    def _do_test_files(self, path):
        """pylint -E on all .py files in path"""
        for fname in listdir(path):
            fpath = join(path, fname)
            if len(fname) > 2 and fpath[-3:] == '.py' and isfile(fpath):
                retcode = subprocess.call(["pylint", "-E", fpath])
                self.assertEqual(0, retcode,
                                 msg='linting required for %s' % fpath)

    @skipUnless(HAVE_PYLINT, "Must have pylint executable installed")
    def test_library(self):
        self._do_test_files('friskby/')

    @skipUnless(HAVE_PYLINT, "Must have pylint executable installed")
    def test_tests_meta(self):
        self._do_test_files('tests/')
