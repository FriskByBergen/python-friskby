from tempfile import NamedTemporaryFile as temp
from unittest import TestCase
from random import random as rnd, randint
import sqlite3
from datetime import datetime as dt
from friskby import TS, FriskbyDao

def rand():
    return round(rnd()*100, 2)

def gen_rand_ts(value=None):
    """Uses value if given, else random"""
    t = TS()
    for _ in range(3):
        if value:
            t.append(value)
        else:
            t.append(rand())
    return t

class DaoTest(TestCase):

    def setUp(self):
        tmpf = temp(delete=False)
        self.fname = tmpf.name + '_db.sql'
        tmpf.close()
        self.dao = FriskbyDao(self.fname)

    def test_created(self):
        q = "SELECT name FROM sqlite_master WHERE type='table';"
        conn = sqlite3.connect(self.fname)
        c = conn.execute(q)
        result = c.fetchall()
        self.assertEqual(1, len(result))
        self.assertEqual('samples', result[0][0])

    def _do_test_num_upl(self, dao, exp_num_all, exp_num_upl, exp_num_nup):
        num_all, num_upl, num_nup = (dao.get_num_rows(),
                                     dao.get_num_rows(uploaded_status=True),
                                     dao.get_num_rows(uploaded_status=False))
        self.assertEqual(exp_num_all, num_all)
        self.assertEqual(exp_num_upl, num_upl)
        self.assertEqual(exp_num_nup, num_nup)

    def test_persist(self):
        num_data = 13
        for _ in range(num_data):
            t10 = gen_rand_ts()
            t25 = gen_rand_ts()
            data = {'PM10': t10, 'PM25': t25}
            self.dao.persist_ts(data)

        self._do_test_num_upl(self.dao, 2*num_data, 0, 2*num_data)

        data = self.dao.get_non_uploaded(limit=30)
        self.assertEqual(2*num_data, len(data))

    def test_mark_uploaded(self):
        num_data = 17
        for _ in range(num_data):
            t10 = gen_rand_ts()
            t25 = gen_rand_ts()
            data = {'PM10': t10, 'PM25': t25}
            self.dao.persist_ts(data)
        print(repr(self.dao))

        self._do_test_num_upl(self.dao, 2*num_data, 0, 2*num_data)

        data = self.dao.get_non_uploaded(limit=30)
        self.assertEqual(30, len(data))
        self.dao.mark_uploaded(data)
        data = self.dao.get_non_uploaded(limit=30)
        self.assertEqual(4, len(data)) # total 34, marked 30
        print(repr(self.dao))

        # test num / num upl / num non-upl
        self._do_test_num_upl(self.dao, 2*num_data, 30, 2*num_data - 30)

    def test_localtime(self):
        t10 = gen_rand_ts()
        t25 = gen_rand_ts()
        now = dt.now()
        data = {'PM10': t10, 'PM25': t25}
        self.dao.persist_ts(data)
        out = self.dao.get_non_uploaded(limit=1)[0]
        delta = now - out[3]
        # checking that we're in the same timezone
        self.assertTrue(abs(delta.total_seconds()) < 1000)

    def test_create_directory_structure(self):
        _tmp_dir = '/tmp/friskby/%d/no/such/dir/here' % randint(2**32, 2**42)
        _fpath = '%s/friskby.sql' % _tmp_dir
        dao = FriskbyDao(_fpath)
        sqlpath = dao.get_path()
        self.assertEqual(_fpath, sqlpath)
        t10 = gen_rand_ts(value=26.8)
        t25 = gen_rand_ts(value=19.90)
        data = {'PM10': t10, 'PM25': t25}
        dao.persist_ts(data)
        # data: 2 elts of (id, value, sensor, timestamp, upl)
        data = dao.get_non_uploaded()
        self.assertEqual(2, len(data))
        db_10, db_25 = data
        if db_10[2] != 'PM10':
            db_25, db_10 = data

        self.assertEqual(26.8, db_10[1])
        self.assertEqual(19.9, db_25[1])

    def test_last_entry(self):
        self.assertIsNone(self.dao.last_entry(uploaded=True))
        self.assertIsNone(self.dao.last_entry(uploaded=False))
        self.assertIsNone(self.dao.last_entry())

        t10 = gen_rand_ts()
        t25 = gen_rand_ts()
        data = {'PM10': t10, 'PM25': t25}
        self.dao.persist_ts(data)
        self.assertIsNone(self.dao.last_entry(uploaded=True))
        self.assertIsNotNone(self.dao.last_entry(uploaded=False))
        self.assertIsNotNone(self.dao.last_entry())
        data = self.dao.get_non_uploaded(limit=30)
        self.dao.mark_uploaded(data)
        self.assertIsNotNone(self.dao.last_entry(uploaded=True))
        self.assertIsNone(self.dao.last_entry(uploaded=False))
        self.assertIsNotNone(self.dao.last_entry())
        t10 = gen_rand_ts()
        t25 = gen_rand_ts()
        data = {'PM10': t10, 'PM25': t25}
        self.dao.persist_ts(data)
        self.assertIsNotNone(self.dao.last_entry(uploaded=True))
        self.assertIsNotNone(self.dao.last_entry(uploaded=False))
        self.assertIsNotNone(self.dao.last_entry())
        # could admittedly also test timestamp, but is hard since dao timestamps
