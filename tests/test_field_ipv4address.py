import unittest
import gateaux
from ipaddress import IPv4Address


class IPv4AddressFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.IPv4AddressField()

    def test_validation(self) -> None:
        field = gateaux.IPv4AddressField()
        self.assertEqual(field.pack(IPv4Address('127.0.0.1')), b'\x7f\x00\x00\x01')

    def test_pack(self) -> None:
        field = gateaux.IPv4AddressField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not an IPv4Address') # type: ignore
        self.assertEqual(field.pack(IPv4Address('127.0.0.1')), b'\x7f\x00\x00\x01')

    def test_unpack(self) -> None:
        field = gateaux.IPv4AddressField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not bytes') # type: ignore
        self.assertEqual(field.unpack(b'\x7f\x00\x00\x01'), IPv4Address('127.0.0.1'))
