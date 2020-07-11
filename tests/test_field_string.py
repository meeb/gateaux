import unittest
import gateaux


class StringFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.StringField()
        self.assertEqual(field.max_length, None)
        field = gateaux.StringField(max_length=12345)
        self.assertEqual(field.max_length, 12345)

    def test_validation(self) -> None:
        field = gateaux.StringField()
        self.assertEqual(field.pack('test'), 'test')
        field = gateaux.StringField(max_length=3)
        self.assertEqual(field.max_length, 3)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('test')

    def test_pack(self) -> None:
        field = gateaux.StringField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(b'not str') # type: ignore
        self.assertEqual(field.pack('test'), 'test')

    def test_unpack(self) -> None:
        field = gateaux.StringField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack(b'not str') # type: ignore
        self.assertEqual(field.unpack('test'), 'test')
