from os import listdir
from os.path import isfile, join
import sys
from unittest import TestCase, skipUnless
import subprocess

try:
    subprocess.call(["pylint", "--version"])
    HAVE_PYLINT = True
except OSError:
    sys.stderr.write('** Warning: could not find Python checker "pylint" - static checks skipped')
    HAVE_PYLINT = False

class PylintTest(TestCase):
    @skipUnless(HAVE_PYLINT, "Must have pylint executable installed")
    def test_library(self):
        module_path = 'python/friskby/'
        for fname in listdir(module_path):
            fpath = join(module_path, fname)
            if len(fname) > 2 and fpath[-3:] == '.py' and isfile(fpath):
                subprocess.check_call(["pylint", "-E", fpath])
