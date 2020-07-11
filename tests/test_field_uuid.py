import unittest
import gateaux
from uuid import UUID


class IPv4NetworkFieldTestCase(unittest.TestCase):

    def test_pack(self) -> None:
        field = gateaux.UUIDField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not a UUID') # type: ignore
        test_uuid = UUID(bytes=b'I\xa2Vf\x1d\xddH\x96\xb2\x05\xa1\xb86~lN')
        self.assertEqual(field.pack(test_uuid),
                         b'I\xa2Vf\x1d\xddH\x96\xb2\x05\xa1\xb86~lN')

    def test_unpack(self) -> None:
        field = gateaux.UUIDField()
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not bytes') # type: ignore
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(b'not 16 bytes') # type: ignore
        test_uuid = UUID(bytes=b'I\xa2Vf\x1d\xddH\x96\xb2\x05\xa1\xb86~lN')
        self.assertEqual(field.unpack(b'I\xa2Vf\x1d\xddH\x96\xb2\x05\xa1\xb86~lN'),
                         test_uuid)
