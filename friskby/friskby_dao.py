from __future__ import print_function

import sys
from os import makedirs
from os.path import abspath, isfile, isdir, split
import sqlite3
from datetime import datetime as dt
from dateutil import parser as dt_parser


def _insert(val, sensor):
    """Returns INSERT query"""
    # TODO make this prepared statement
    query = "INSERT INTO samples (id, value, sensor, timestamp) VALUES (NULL, %f, '%s', '%s');"
    return query % (val, sensor, dt.utcnow())


class FriskbyDao(object):
    """The *FriskbyDao* is a data access object that currently persists measured
    data to an SQLITE file using the `sqlite3` Python module.

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
    unit).  The `uploaded` flag signifies whether the measurement has been
    uploaded

    """
    # TODO make FriskbyDao a context manager so we can:
    # with FriskbyDao(path) as dao:
    #    dao.get_non_uploaded(...)
    #    submitter.post(...)
    #    dao.mark_uploaded(...)

    def __init__(self, sql_path):
        """The sqlite db has a table called 'samples' with schema
        id, value, sensor, timestamp, uploaded
        """
        self._sql_path = abspath(sql_path)
        self.__init_sql()

    def get_path(self):
        return self._sql_path

    def __init_sql(self):
        if isfile(self._sql_path):
            return # nothing to do

        _path, _ = split(self._sql_path)
        if not isdir(_path):
            makedirs(_path) # equivalent to `mkdir -p _path`
        if not isfile(self._sql_path):
            print('No database, constructing new: %s.' % self._sql_path)
            _id = '`id` INTEGER PRIMARY KEY'
            _val = '`value` FLOAT NOT NULL'
            _sen = '`sensor` TEXT NOT NULL'
            _date = '`timestamp` TEXT NOT NULL'
            _upl = '`uploaded` BOOL DEFAULT 0'
            _create = 'CREATE TABLE samples (%s, %s, %s, %s, %s);'
            schema = _create % (_id, _val, _sen, _date, _upl)
            conn = sqlite3.connect(self._sql_path)
            conn.execute(schema)
            conn.close()

    def get_num_rows(self, uploaded_status=None):
        """Gets num rows in sql storage.  If uploaded_status is set to True, we
        fetch number of rows that are marked uploaded, if uploaded_status is set
        to False, we fetch number of rows that are marked as not uploaded.
        """
        query = 'SELECT COUNT(uploaded) FROM samples'
        if uploaded_status is not None:
            if uploaded_status:
                query += ' WHERE uploaded'
            else:
                query += ' WHERE NOT uploaded'
        query += ';'
        conn = sqlite3.connect(self._sql_path)
        result = conn.execute(query)
        num = result.fetchone()[0]
        conn.close()
        return num


    def get_non_uploaded(self, limit=100):
        sub_q = "id, value, sensor, datetime(timestamp, 'localtime'), uploaded"
        query = 'SELECT %s FROM samples WHERE NOT `uploaded` LIMIT %d;'

        conn = sqlite3.connect(self._sql_path)
        result = conn.execute(query % (sub_q, limit))
        data = result.fetchall()
        conn.close()
        print('dao fetched %d rows of non-uploaded data' % len(data))
        sys.stdout.flush()
        for i in range(len(data)):
            id_, val_, sens_, dt_, upl_ = data[i]
            data[i] = id_, val_, sens_, dt_parser.parse(dt_), upl_
        return data

    def persist_ts(self, data):
        """Save data to underlying storage.

        Data should be on form {'PM10': TS, 'PM25': TS, ...}, where the TS are
        timeseries, that is, they should have a median: TS->float function.

        """
        queries = []
        for sensor, ts in data.items():
            queries.append(_insert(ts.median(), sensor))
        conn = sqlite3.connect(self._sql_path)
        for query in queries:
            conn.execute(query)
        conn.commit()
        conn.close()

    def last_entry(self, uploaded=None):
        """Returns timestamp of the last entry in the dao, or None if no entry matches
        the criterion.  If uploaded is non-None, then a truthy value will return the
        last uploaded, and a falsy value will give the last non-uploaded entry.
        """
        query_pre = 'SELECT timestamp FROM samples'
        query_mid = ' WHERE `uploaded` = %d' % (1 if uploaded else 0)
        query_post = ' ORDER BY timestamp DESC LIMIT 1'
        query = query_pre + query_post
        return_value = None
        if uploaded is not None:
            query = query_pre + query_mid + query_post
        conn = sqlite3.connect(self._sql_path)
        result = conn.execute(query)
        data = result.fetchall()
        if data:
            return_value = dt_parser.parse(data[0][0])
        conn.close()
        return return_value


    def mark_uploaded(self, data):
        print('dao marking ...')
        sys.stdout.flush()
        query = 'UPDATE samples SET uploaded=1 WHERE id=%s'

        conn = sqlite3.connect(self._sql_path)
        conn.execute('begin')
        for row in data:
            # id, value, sensor, timestamp, uploaded
            id_ = row[0]
            conn.execute(query % id_)
        conn.commit()
        conn.close()


    def __repr__(self):
        try:
            num, num_up = self.get_num_rows(), self.get_num_rows(uploaded_status=True)
            fmt = 'FriskbyDao(num_rows=%s, non_uploaded=%s, path=%s)'
            return fmt % (num, num_up, self._sql_path)
        except:
            return 'FriskbyDao(path=%s)' % (self._sql_path)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(FriskbyDao(sys.argv[1]))
    else:
        sys.exit('Need a path to an sqlite database.')
