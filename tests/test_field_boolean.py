import unittest
import gateaux


class BooleanFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.BooleanField()

    def test_validation(self) -> None:
        field = gateaux.BooleanField()
        self.assertEqual(field.pack(True), True)

    def test_pack(self) -> None:
        field = gateaux.BooleanField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not boolean') # type: ignore
        self.assertEqual(field.pack(True), True)

    def test_unpack(self) -> None:
        field = gateaux.BooleanField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not boolean') # type: ignore
        self.assertEqual(field.unpack(True), True)
