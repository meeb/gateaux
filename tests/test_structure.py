from typing import Tuple
import unittest
import fdb.tuple
import gateaux


class MockFoundationSubspace:
    '''
        A mock FoundationDB directory or subspace layer instance which supports test
        data storage. When calling pack() and unpack() this will use FoundationDB's
        fdb.tuple.pack. During testing this mock class just optionally prefixes the
        response with \x00\x00 to simulate a real directory prefix. As we're not
        actually talking to a FoundationDB cluster during testing this is sufficient
        as we only need to test gateaux's packing and unpacking, not FoundationDB.
    '''

    def __init__(self, *args, **kwargs) -> None:
        self.data:dict = {}

    def __getitem__(self, key: bytes) -> bytes:
        return self.data.get(key)

    def __setitem__(self, key: bytes, value: bytes) -> bool:
        self.data[key] = value
        return True

    def __delitem__(self, key: bytes) -> bool:
        del self.data[key]
        return True

    def pack(self, v: Tuple, prefix: bool = True) -> bytes:
        '''
            Pack a tuple and optionally prepend \x00\x00 to simulate a FoundationDB
            directory.
        '''
        if prefix:
            return b'\x00\x00' + fdb.tuple.pack(v)
        else:
            return fdb.tuple.pack(v)

    def unpack(self, v:bytes, prefix: bool = True) -> tuple:
        '''
            Truncate the first two bytes then unpack the tuple.
        '''
        if prefix:
            assert(v[0:2] == b'\x00\x00')
            return fdb.tuple.unpack(v[2:])
        else:
            return fdb.tuple.unpack(v)


class MockSubspaceTestCase(unittest.TestCase):

    def test_mock_directory(self) -> None:
        mock_ss = MockFoundationSubspace()
        mock_ss[b'test'] = b'test'
        self.assertEqual(mock_ss[b'test'], b'test')
        del mock_ss[b'test']
        self.assertEqual(mock_ss[b'test'], None)
        packed = mock_ss.pack(('test', 'tuple'))
        self.assertEqual(packed, b'\x00\x00\x02test\x00\x02tuple\x00')
        unpacked = mock_ss.unpack(packed)
        self.assertEqual(unpacked, ('test', 'tuple'))
        packed = mock_ss.pack(('test', 'tuple'), prefix=False)
        self.assertEqual(packed, b'\x02test\x00\x02tuple\x00')
        unpacked = mock_ss.unpack(packed, prefix=False)
        self.assertEqual(unpacked, ('test', 'tuple'))


class StructureTestCase(unittest.TestCase):

    def test_validation_key(self) -> None:
        mock_ss = MockFoundationSubspace()
        class InvalidKeyTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), object())
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            InvalidKeyTestStructure(mock_ss)
        class NoKeyTestStructure(gateaux.Structure):
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            NoKeyTestStructure(mock_ss)
        class EmptyKeyTestStructure(gateaux.Structure):
            key = ()
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            EmptyKeyTestStructure(mock_ss)
        class ValidKeyTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        ValidKeyTestStructure(mock_ss)

    def test_validation_value(self) -> None:
        mock_ss = MockFoundationSubspace()
        class InvalidValueTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(), object())
        with self.assertRaises(gateaux.errors.StructureError):
            InvalidValueTestStructure(mock_ss)
        class NoValueTestStructure(gateaux.Structure):
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            NoValueTestStructure(mock_ss)
        class EmptyValueTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(),)
            value = ()
        # Empty value is permitted
        EmptyValueTestStructure(mock_ss)
        class ValidValueTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        ValidValueTestStructure(mock_ss)

    def test_pack(self) -> None:
        mock_ss = MockFoundationSubspace()
        class ValidTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        valid = ValidTestStructure(mock_ss)
        with self.assertRaises(gateaux.errors.ValidationError):
            # Too many
            valid._pack(valid.key, (b'a', b'b', b'c'))
        with self.assertRaises(gateaux.errors.ValidationError):
            # Wrong type
            valid._pack(valid.key, (b'a', 1))
        packed = valid._pack(valid.key, (b'a', b'b'))
        self.assertEqual(packed, b'\x00\x00\x01a\x00\x01b\x00')
        # Empty value
        class EmptyValueTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = ()
        emptyvalue = ValidTestStructure(mock_ss)
        emptyvalue._pack(valid.value, ())

    def test_unpack(self) -> None:
        mock_ss = MockFoundationSubspace()
        class ValidTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        valid = ValidTestStructure(mock_ss)
        with self.assertRaises(gateaux.errors.ValidationError):
            # Too many
            valid._unpack(valid.key, b'\x00\x00\x01a\x00\x01b\x00\x01c\x00')
        with self.assertRaises(gateaux.errors.ValidationError):
            # Wrong type
            valid._unpack(valid.key, b'\x00\x00\x01a\x00\x02b\x00')
        unpacked = valid._unpack(valid.key, b'\x00\x00\x01a\x00\x01b\x00')
        self.assertEqual(unpacked, (b'a', b'b'))

    def test_pack_key_dict(self) -> None:
        mock_ss = MockFoundationSubspace()
        # Structure with no key field names
        class NoNamesStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        noname = NoNamesStructure(mock_ss)
        with self.assertRaises(gateaux.errors.StructureError):
            noname.pack_key_dict({'field1': b'test', 'field2': b'test'})
        # Strucuture with key field names
        class NamedStructure(gateaux.Structure):
            key = (gateaux.BinaryField(name='field1'),
                   gateaux.BinaryField(name='field2'))
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        named = NamedStructure(mock_ss)
        with self.assertRaises(gateaux.errors.ValidationError):
            named.pack_key_dict((b'not a', b'dict')) # type: ignore
        with self.assertRaises(gateaux.errors.ValidationError):
            named.pack_key_dict({'field1': b'test', 'invalid': b'test'})
        packed = named.pack_key_dict({'field1': b'test', 'field2': b'test'})
        self.assertEqual(packed, b'\x00\x00\x01test\x00\x01test\x00')
        packed = named.pack_key_dict({'field2': b'test', 'field1': b'test'})
        self.assertEqual(packed, b'\x00\x00\x01test\x00\x01test\x00')

    def test_unpack_key_dict(self) -> None:
        mock_ss = MockFoundationSubspace()
        # Structure with no key field names
        class NoNamesStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        noname = NoNamesStructure(mock_ss)
        with self.assertRaises(gateaux.errors.StructureError):
            noname.unpack_key_dict(b'\x00\x00\x01test\x00\x01test\x00')
        # Strucuture with key field names
        class NamedStructure(gateaux.Structure):
            key = (gateaux.BinaryField(name='field1'),
                   gateaux.BinaryField(name='field2'))
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        named = NamedStructure(mock_ss)
        with self.assertRaises(gateaux.errors.ValidationError):
            named.unpack_key_dict('not bytes') # type: ignore
        unpacked = named.unpack_key_dict(b'\x00\x00\x01test\x00\x01test\x00')
        self.assertEqual(unpacked, {'field1': b'test', 'field2': b'test'})

    def test_pack_value_dict(self) -> None:
        mock_ss = MockFoundationSubspace()
        # Structure with no value field names
        class NoNamesStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        noname = NoNamesStructure(mock_ss)
        with self.assertRaises(gateaux.errors.StructureError):
            noname.pack_value_dict({'field1': b'test', 'field2': b'test'})
        # Strucuture with value field names
        class NamedStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(name='value1'),
                     gateaux.BinaryField(name='value2'))
        named = NamedStructure(mock_ss)
        with self.assertRaises(gateaux.errors.ValidationError):
            named.pack_value_dict((b'not a', b'dict')) # type: ignore
        with self.assertRaises(gateaux.errors.ValidationError):
            named.pack_value_dict({'value1': b'test', 'invalid': b'test'})
        with self.assertRaises(gateaux.errors.ValidationError):
            named.pack_value_dict({'value1': b'test'})
        packed = named.pack_value_dict({'value1': b'test1', 'value2': b'test2'})
        self.assertEqual(packed, b'\x00\x00\x01test1\x00\x01test2\x00')
        packed = named.pack_value_dict({'value2': b'test2', 'value1': b'test1'})
        self.assertEqual(packed, b'\x00\x00\x01test1\x00\x01test2\x00')

    def test_unpack_value_dict(self) -> None:
        mock_ss = MockFoundationSubspace()
        # Structure with no value field names
        class NoNamesStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        noname = NoNamesStructure(mock_ss)
        with self.assertRaises(gateaux.errors.StructureError):
            noname.unpack_value_dict(b'\x00\x00\x01test\x00\x01test\x00')
        # Strucuture with value field names
        class NamedStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(name='value1'),
                     gateaux.BinaryField(name='value2'))
        named = NamedStructure(mock_ss)
        with self.assertRaises(gateaux.errors.ValidationError):
            named.unpack_value_dict('not bytes') # type: ignore
        unpacked = named.unpack_value_dict(b'\x00\x00\x01test1\x00\x01test2\x00')
        self.assertEqual(unpacked, {'value1': b'test1', 'value2': b'test2'})

    def test_interface(self) -> None:
        mock_ss = MockFoundationSubspace()
        class ValidTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(), gateaux.BinaryField(),)
            value = (gateaux.BinaryField(), gateaux.BinaryField(),)
        test = ValidTestStructure(mock_ss)
        with self.assertRaises(gateaux.errors.ValidationError):
            # Empty
            test.pack_key(())
        with self.assertRaises(gateaux.errors.ValidationError):
            # Too many
            test.pack_key((b'a', b'b', b'b'))
        with self.assertRaises(gateaux.errors.ValidationError):
            # Empty
            test.pack_value(())
        with self.assertRaises(gateaux.errors.ValidationError):
            # Too many
            test.pack_value((b'a', b'b', b'b'))
        # 0 < len(key_values) <= len(structure.key) is allowed
        test.pack_key((b'test',))
        # Where as for value fields, len(key_values) == len(structure.values)
        with self.assertRaises(gateaux.errors.ValidationError):
            test.pack_value((b'test',))
        # Validate packing
        packed_key = test.pack_key((b'test', b'test'))
        self.assertEqual(packed_key, b'\x00\x00\x01test\x00\x01test\x00')
        unpacked_key = test.unpack_key(packed_key)
        self.assertEqual(unpacked_key, (b'test', b'test'))
        packed_value = test.pack_value((b'test', b'test'))
        self.assertEqual(packed_value, b'\x00\x00\x01test\x00\x01test\x00')
        unpacked_value = test.unpack_value(packed_value)
        self.assertEqual(unpacked_value, (b'test', b'test'))

    def test_description(self) -> None:
        mock_ss = MockFoundationSubspace()
        class ValidTestStructure(gateaux.Structure):
            '''test doc string'''
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        test = ValidTestStructure(mock_ss)
        desc = test.description
        self.assertEqual(desc['name'], 'ValidTestStructure')
        self.assertEqual(desc['doc'], 'test doc string')
        # Field description testing is in test_field_base, no need to dupe here
        self.assertIsInstance(desc['key'], list)
        self.assertEqual(len(desc['key']), 1)
        self.assertIsInstance(desc['key'][0], dict)
        self.assertIsInstance(desc['value'], list)
        self.assertEqual(len(desc['value']), 1)
        self.assertIsInstance(desc['value'][0], dict)
