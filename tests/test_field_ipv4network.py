import unittest
import gateaux
from ipaddress import IPv4Network


class IPv4NetworkFieldTestCase(unittest.TestCase):

    def test_pack(self) -> None:
        field = gateaux.IPv4NetworkField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not a IPv4Network') # type: ignore
        self.assertEqual(field.pack(IPv4Network('127.0.0.1/32')), b'\x7f\x00\x00\x01 ')

    def test_unpack(self) -> None:
        field = gateaux.IPv4NetworkField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not bytes') # type: ignore
        self.assertEqual(field.unpack(b'\x7f\x00\x00\x01 '),
                         IPv4Network('127.0.0.1/32'))
