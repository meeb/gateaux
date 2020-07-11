import unittest
import gateaux


class EnumFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        ENUM1 = 1
        ENUM2 = 2
        ENUM3 = 3
        ENUMS = (ENUM1, ENUM2, ENUM3)
        field = gateaux.EnumField(members=ENUMS)
        self.assertEqual(field.members, ENUMS)
        with self.assertRaises(gateaux.errors.FieldError):
            gateaux.EnumField()

    def test_validation(self) -> None:
        field = gateaux.EnumField(members=(1, 2, 3))
        self.assertEqual(field.pack(1), 1)
        self.assertEqual(field.pack(2), 2)
        self.assertEqual(field.pack(3), 3)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(0)
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack(4)

    def test_pack(self) -> None:
        field = gateaux.EnumField(members=(1, 2, 3))
        with self.assertRaises(gateaux.errors.ValidationError):
            field.pack('not int') # type: ignore
        self.assertEqual(field.pack(1), 1)

    def test_unpack(self) -> None:
        field = gateaux.EnumField(members=(1, 2, 3))
        with self.assertRaises(gateaux.errors.ValidationError):
            field.unpack('not int') # type: ignore
        self.assertEqual(field.unpack(1), 1)
