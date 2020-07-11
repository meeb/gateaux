import unittest
import gateaux


class FloatFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.FloatField()
        self.assertEqual(field.min_value, None)
        self.assertEqual(field.max_value, None)
        field = gateaux.FloatField(min_value=1234, max_value=5678)
        self.assertEqual(field.min_value, 1234)
        self.assertEqual(field.max_value, 5678)
        with self.assertRaises(gateaux.errors.FieldError):
            gateaux.FloatField(min_value=5678, max_value=1234)

    def test_validation(self) -> None:
        field = gateaux.FloatField()
        self.assertEqual(field.pack(1.23), 1.23)
        field = gateaux.FloatField(min_value=123)
        self.assertEqual(field.min_value, 123)
        self.assertEqual(field.pack(123.0), 123.0)
        self.assertEqual(field.pack(123.456), 123.456)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(122.9)
        field = gateaux.FloatField(max_value=456)
        self.assertEqual(field.max_value, 456)
        self.assertEqual(field.pack(456.0), 456.0)
        self.assertEqual(field.pack(455.9), 455.9)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(456.1)
        field = gateaux.FloatField(min_value=123, max_value=456)
        self.assertEqual(field.pack(123.0), 123.0)
        self.assertEqual(field.pack(455.5), 455.5)
        self.assertEqual(field.pack(333.9), 333.9)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(122.9)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(456.1)

    def test_pack(self) -> None:
        field = gateaux.FloatField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(1) # type: ignore
        self.assertEqual(field.pack(123.0), 123.0)

    def test_unpack(self) -> None:
        field = gateaux.FloatField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack(1) # type: ignore
        self.assertEqual(field.unpack(123.0), 123.0)
