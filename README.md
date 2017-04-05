# python-friskby [![Build Status](https://travis-ci.org/FriskByBergen/python-friskby.svg?branch=master)](https://travis-ci.org/FriskByBergen/python-friskby)

## Overview

The _friskby_ module is a Python module for reading from external sensors
(currently, only the `SDS011` sensor is supported), store measurements to a
temporary database and post the measurements to a webserver.

In the future we will add other sensors for temperature, relative humidity,
barometric pressure, noise level detection, luminosity, etc, and will post data
for such sensors to a webserver.


## Install

To install, you may use pip:

```bash
sudo pip install friskby
```

Or from source:

```bash
git clone https://github.com/FriskByBergen/python-friskby.git
cd python-friskby
sudo pip install .
```

## Description of functionality

The module consists of three primary features:

1. sampling
2. submitting
3. updating

### FriskbySampler

The FriskbySampler is a module that connects to the sensor and samples
information about the weather, air, climate or surrounding environment, and
stores the data to the *FriskbyDao*.  The *FriskbyDao* is a [data access
object](https://en.wikipedia.org/wiki/Data_access_object) that currently
persists measured data to an SQLITE file using the
[`sqlite3`](https://docs.python.org/2/library/sqlite3.html) Python module.

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

### FriskbySubmitter

The FriskbySubmitter reads non-uploaded measurements from the FriskbyDao and
submits these measurements to the prescribed webserver.  The URL and API key for
the webserver is defined in a config file provided by the caller.  The submitter
uses the `requests` module in Python (it is recommended that one has
`requests>=2.13.0`, which is the latest one).

### FriskbyManager

The job of the FriskbyManager is to read the aforementioned config file, contact
the webserver and ask for today's news.  They are rare, but may contain
reconfiguration of API keys, URL's and occasionally requests that the client
updates itself.

## RPiParticle
These features mentioned above are used from the
[RPiParticle](https://github.com/FriskByBergen/RPiParticle) project, but can
also be used by other daemons or cron jobs.  The RPiParticle launches one
systemd job for each of the above.
