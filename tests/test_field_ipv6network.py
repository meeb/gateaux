import unittest
import gateaux
from ipaddress import IPv6Network


class IPv6NetworkFieldTestCase(unittest.TestCase):

    def test_pack(self) -> None:
        field = gateaux.IPv6NetworkField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not a IPv6Network') # type: ignore
        self.assertEqual(field.pack(IPv6Network('1::/64')),
            b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@')

    def test_unpack(self) -> None:
        field = gateaux.IPv6NetworkField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not bytes') # type: ignore
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack(b'not 17 bytes')
        self.assertEqual(field.unpack(
            b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@'),
            IPv6Network('1::/64'))
