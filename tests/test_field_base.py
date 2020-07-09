import unittest
import gateaux


class BaseFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.BaseField()
        self.assertEqual(field.name, '')
        self.assertEqual(field.help_text, '')
        self.assertEqual(field.optional, False)
        field = gateaux.BaseField(name='name', help_text='help', optional=True)
        self.assertEqual(field.name, 'name')
        self.assertEqual(field.help_text, 'help')
        self.assertEqual(field.optional, True)
        with self.assertRaises(TypeError):
            gateaux.BaseField(name=b'not a string')
        with self.assertRaises(TypeError):
            gateaux.BaseField(help_text=b'not a string')
        with self.assertRaises(TypeError):
            gateaux.BaseField(optional=b'not a boolean')
        with self.assertRaises(ValueError):
            gateaux.BaseField(unknown_kwarg='test')

    def test_interface(self) -> None:
        field = gateaux.BaseField()
        with self.assertRaises(NotImplementedError):
            field.validate('test')
        with self.assertRaises(NotImplementedError):
            field.pack('test')
        with self.assertRaises(NotImplementedError):
            field.unpack('test')
