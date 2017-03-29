"""The friskby module
"""

from __future__ import absolute_import

from serial import SerialException
from .device_config import DeviceConfig
from .friskby_dao import FriskbyDao
from .friskby_sampler import FriskbySampler
from .friskby_runner import FriskbyRunner
from .friskby_submitter import FriskbySubmitter
from .os_release import sys_info

try:
    from sds011 import SDS011
except ImportError as err:
    import sys
    sys.stderr.write('Missing SDS011 library: %s\n' % str(err))
    sys.stderr.write('Using mock library.\n')
    sys.stderr.flush()
    from .mock_sds011 import SDS011
except SerialException as err:
    import sys
    sys.stderr.write('Using mock SDS011 serial device: %s\n' % str(err))
    sys.stderr.write('Using mock library.\n')
    sys.stderr.flush()
    from .mock_sds011 import SDS011

from .ts import TS

__all__ = ['FriskbyDao', 'FriskbySampler', 'FriskbySubmitter', 'FriskbyRunner',
           'SDS011', 'TS', 'DeviceConfig', 'sys_info']

__version__ = '0.63.0'
