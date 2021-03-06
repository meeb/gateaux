import unittest
import gateaux


class BaseFieldTestCase(unittest.TestCase):

    def test_constructor(self) -> None:
        field = gateaux.BaseField()
        self.assertIsInstance(field.data_type, object)
        self.assertEqual(field.name, '')
        self.assertEqual(field.help_text, '')
        self.assertEqual(field.null, False)
        self.assertEqual(field.default, None)
        field = gateaux.BaseField(name='name', help_text='help', null=True,
                                  default='test')
        self.assertEqual(field.name, 'name')
        self.assertEqual(field.help_text, 'help')
        self.assertEqual(field.null, True)
        self.assertEqual(field.default, 'test')
        with self.assertRaises(TypeError):
            gateaux.BaseField(name=b'not a string')
        with self.assertRaises(TypeError):
            gateaux.BaseField(help_text=b'not a string')
        with self.assertRaises(TypeError):
            gateaux.BaseField(name=b'not a boolean')
        with self.assertRaises(ValueError):
            gateaux.BaseField(unknown_kwarg='test')

    def test_interface(self) -> None:
        field = gateaux.BaseField()
        with self.assertRaises(NotImplementedError):
            field.pack('test')
        with self.assertRaises(NotImplementedError):
            field.unpack('test')

    def test_null_and_default(self) -> None:
        mandatory_field = gateaux.BaseField()
        with self.assertRaises(gateaux.errors.ValidationError):
            mandatory_field.validate_packed(None)
        self.assertEqual(mandatory_field.validate_packed(b'test'), b'test')
        optional_field = gateaux.BaseField(null=True)
        self.assertEqual(optional_field.validate_packed(None), None)
        optional_default_field = gateaux.BaseField(null=True, default=b'default')
        self.assertEqual(optional_default_field.validate_packed(None), b'default')
        mandatory_default_field = gateaux.BaseField(default=b'default')
        self.assertEqual(mandatory_default_field.validate_packed(b'test'), b'test')

    def test_description(self) -> None:
        field = gateaux.BaseField(
            name='test name',
            help_text='test help text',
            null=False,
            default='test default'
        )
        desc = field.description
        self.assertEqual(desc['field'], 'BaseField')
        self.assertEqual(desc['name'], 'test name')
        self.assertEqual(desc['help_text'], 'test help text')
        self.assertEqual(desc['null'], False)
        self.assertEqual(desc['default'], 'test default')
