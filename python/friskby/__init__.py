"""The friskby module
"""

from __future__ import absolute_import

from serial import SerialException
from .git_module import GitModule
from .device_config import DeviceConfig
from .dist import files, directories
from .friskby_dao import FriskbyDao
from .os_release import sys_info

# if _os_getenv("FRISKBY_TEST"):
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


from .service_config import ServiceConfig
from .ts import TS
from .wifi_config import Network, WifiConfig

__all__ = ['FriskbyDao', 'SDS011', 'ServiceConfig', 'TS',
           'GitModule', 'DeviceConfig', 'sys_info', 'WifiConfig', 'Network']

__version__ = '0.60.0'
