import unittest
import gateaux


class BinaryFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.BinaryField()
        self.assertEqual(field.max_length, None)
        field = gateaux.BinaryField(max_length=12345)
        self.assertEqual(field.max_length, 12345)

    def test_validation(self) -> None:
        field = gateaux.BinaryField()
        self.assertEqual(field.pack(b'test'), b'test')
        field = gateaux.BinaryField(max_length=3)
        self.assertEqual(field.max_length, 3)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(b'test')

    def test_pack(self) -> None:
        field = gateaux.BinaryField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not bytes') # type: ignore
        self.assertEqual(field.pack(b'test'), b'test')

    def test_unpack(self) -> None:
        field = gateaux.BinaryField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not bytes') # type: ignore
        self.assertEqual(field.unpack(b'test'), b'test')
