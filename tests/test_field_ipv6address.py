import unittest
import gateaux
from ipaddress import IPv6Address


class IPv6AddressFieldTestCase(unittest.TestCase):

    def test_pack(self) -> None:
        field = gateaux.IPv6AddressField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not an IPv6Address') # type: ignore
        self.assertEqual(field.pack(IPv6Address('::1')),
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')

    def test_unpack(self) -> None:
        field = gateaux.IPv6AddressField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not bytes') # type: ignore
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack(b'not 16 bytes')
        self.assertEqual(field.unpack(
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'),
            IPv6Address('::1'))
