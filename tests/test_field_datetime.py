import unittest
import gateaux
from datetime import datetime
from calendar import timegm
import pytz


class DateTimeFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.DateTimeField()

    def test_validation(self) -> None:
        field = gateaux.DateTimeField()
        dt = datetime.utcnow().replace(microsecond=0)
        td_utc = pytz.utc.localize(dt)
        ts = int(timegm(td_utc.timetuple()))
        ts_ms = ts + (td_utc.microsecond / 100000)
        self.assertEqual(field.pack(td_utc), ts_ms)

    def test_pack(self) -> None:
        field = gateaux.DateTimeField()
        dt = datetime.utcnow().replace(microsecond=0)
        td_utc = pytz.utc.localize(dt)
        ts = int(timegm(td_utc.timetuple()))
        ts_ms = ts + (td_utc.microsecond / 100000)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not datetime') # type: ignore
        self.assertEqual(field.pack(td_utc), ts_ms)

    def test_unpack(self) -> None:
        field = gateaux.DateTimeField()
        dt = datetime.utcnow().replace(microsecond=0)
        td_utc = pytz.utc.localize(dt)
        ts = int(timegm(td_utc.timetuple()))
        ts_ms = ts + (td_utc.microsecond / 100000)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not int') # type: ignore
        self.assertEqual(field.unpack(ts_ms), td_utc)
