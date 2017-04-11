"""The friskby module.

The _friskby_ module is a Python module for reading from external sensors
(currently, only the `SDS011` sensor is supported), store measurements to a
temporary database and post the measurements to a webserver.

In the future we will add other sensors for temperature, relative humidity,
barometric pressure, noise level detection, luminosity, etc, and will post data
for such sensors to a webserver.

# Overview of functionality

The module consists of three primary features:

1. sampling
2. submitting
3. updating

# FriskbySampler

The FriskbySampler is a module that connects to the sensor and samples
information about the weather, air, climate or surrounding environment, and
stores the data to the *FriskbyDao*.  The *FriskbyDao* is a data access object
that currently persists measured data to an SQLITE file using the `sqlite3`
Python module.

The underlying database _scheme_ is simple:

```sql
CREATE TABLE samples (
    `id` INTEGER PRIMARY KEY,
    `value` FLOAT NOT NULL,
    `sensor` TEXT NOT NULL,
    `timestamp` TEXT NOT NULL,
    `uploaded` BOOL DEFAULT 0
    );
```

The `sensor` describes contains the sensor ID and describes what type of
measurement has been done.  The value is its value (in an assumed known (SI)
unit).  The `uploaded` flag signifies whether the measurement has been uploaded,
which is dealt with by the

# FriskbySubmitter

The FriskbySubmitter reads non-uploaded measurements from the FriskbyDao and
submits these measurements to the prescribed webserver.  The URL and API key for
the webserver is defined in a config file provided by the caller.  The submitter
uses the `requests` module in Python (it is recommended that one has
`requests>=2.13.0`, which is the latest one).

# FriskbyManager

The job of the FriskbyManager is to read the aforementioned config file, contact
the webserver and ask for today's news.  They are rare, but may contain
reconfiguration of API keys, URL's and occasionally requests that the client
updates itself.

"""

from __future__ import absolute_import

from serial import SerialException
from .device_config import DeviceConfig
from .friskby_dao import FriskbyDao
from .friskby_sampler import FriskbySampler
from .friskby_manager import FriskbyManager
from .friskby_submitter import FriskbySubmitter
from .os_release import sys_info
from .ts import TS

from .sensors import SDS011

VERSION = '0.67.0'
__all__ = ['FriskbyDao', 'FriskbySampler', 'FriskbySubmitter', 'FriskbyManager',
           'TS', 'DeviceConfig', 'sys_info']

__version__ = VERSION
