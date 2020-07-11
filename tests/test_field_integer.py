import unittest
import gateaux


class IntegerFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.IntegerField()
        self.assertEqual(field.min_value, None)
        self.assertEqual(field.max_value, None)
        field = gateaux.IntegerField(min_value=1234, max_value=5678)
        self.assertEqual(field.min_value, 1234)
        self.assertEqual(field.max_value, 5678)
        with self.assertRaises(gateaux.errors.FieldError):
            gateaux.IntegerField(min_value=5678, max_value=1234)

    def test_validation(self) -> None:
        field = gateaux.IntegerField()
        self.assertEqual(field.pack(1), 1)
        field = gateaux.IntegerField(min_value=123)
        self.assertEqual(field.min_value, 123)
        self.assertEqual(field.pack(123), 123)
        self.assertEqual(field.pack(124), 124)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(122)
        field = gateaux.IntegerField(max_value=456)
        self.assertEqual(field.max_value, 456)
        self.assertEqual(field.pack(456), 456)
        self.assertEqual(field.pack(455), 455)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(457)
        field = gateaux.IntegerField(min_value=123, max_value=456)
        self.assertEqual(field.pack(123), 123)
        self.assertEqual(field.pack(456), 456)
        self.assertEqual(field.pack(333), 333)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(122)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(457)

    def test_pack(self) -> None:
        field = gateaux.IntegerField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not int') # type: ignore
        self.assertEqual(field.pack(123), 123)

    def test_unpack(self) -> None:
        field = gateaux.IntegerField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not int') # type: ignore
        self.assertEqual(field.unpack(123), 123)
