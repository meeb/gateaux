import unittest
import gateaux
from datetime import datetime
from calendar import timegm
import pytz


class DateTimeFieldTestCase(unittest.TestCase):

    def test_pack(self) -> None:
        field = gateaux.DateTimeField()
        dt = datetime.utcnow()
        td_utc = pytz.utc.localize(dt)
        ts = int(timegm(td_utc.timetuple()))
        ts_ms = ts + (td_utc.microsecond / 1000000)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not datetime') # type: ignore
        self.assertEqual(field.pack(td_utc), ts_ms)

    def test_unpack(self) -> None:
        field = gateaux.DateTimeField()
        dt = datetime.utcnow()
        td_utc = pytz.utc.localize(dt)
        ts = int(timegm(td_utc.timetuple()))
        ts_ms = ts + (td_utc.microsecond / 1000000)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not int') # type: ignore
        self.assertEqual(field.unpack(ts_ms), td_utc)
