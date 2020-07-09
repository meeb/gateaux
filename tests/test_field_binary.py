import unittest
import gateaux


class BinaryFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.BinaryField()
        self.assertEqual(field.name, '')
        self.assertEqual(field.help_text, '')
        self.assertEqual(field.optional, False)
        self.assertEqual(field.max_length, 0)
        field = gateaux.BinaryField(max_length=12345)
        self.assertEqual(field.max_length, 12345)

    def test_validation(self) -> None:
        field = gateaux.BinaryField()
        field.pack(b'test')
        field = gateaux.BinaryField(max_length=3)
        with self.assertRaises(gateaux.errors.GateauxValidationError):
            field.pack(b'test')

    def test_pack(self) -> None:
        field = gateaux.BinaryField()
        self.assertEqual(field.pack(b'test'), b'test')

    def test_unpack(self) -> None:
        field = gateaux.BinaryField()
        self.assertEqual(field.unpack(b'test'), b'test')
