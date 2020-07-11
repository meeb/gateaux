from typing import Tuple
import unittest
import fdb.tuple
import gateaux


class MockFoundationDBConnection:
    '''
        A mock FoundationDB connection for testing. The only feature gateaux uses from
        this is fdb.directory.create_or_open(...) so we can create a bare minimum
        example for a mock testing interface.
    '''

    def __init__(self) -> None:
        class Directory:
            def create_or_open(self, path:Tuple[str, ...]) -> MockFoundationDBDirectory:
                return MockFoundationDBDirectory(path)
        self.directory = Directory()


class MockFoundationDBDirectory:
    '''
        A mock FoundationDB directory layer instance which supports test data storage.
        When calling pack() and unpack() this will use FoundationDB's fdb.tuple.pack.
        During testing this mock class just prefixes the response with \x00\x00 to
        simulate a real directory prefix. As we're not actually talking to a
        FoundationDB cluster during testing this is sufficient aswe only need to test
        gateaux's packing and unpacking, not FoundationDB itself.
    '''

    def __init__(self, path:Tuple[str, ...]) -> None:
        self.path:Tuple[str, ...] = path
        self.data:dict = {}

    def __getitem__(self, key:bytes) -> bytes:
        return self.data.get(key)

    def __setitem__(self, key:bytes, value:bytes) -> bool:
        self.data[key] = value
        return True

    def __delitem__(self, key:bytes) -> bool:
        del self.data[key]
        return True

    def pack(self, v:Tuple) -> bytes:
        '''
            Pack a tuple and prepend \x00\x00 to simulate a FoundationDB directory.
        '''
        return b'\x00\x00' + fdb.tuple.pack(v)

    def unpack(self, v:bytes) -> tuple:
        '''
            Truncate the first two bytes then unpack the tuple.
        '''
        assert(v[0:2] == b'\x00\x00')
        return fdb.tuple.unpack(v[2:])


class MockConnectionTestCase(unittest.TestCase):

    def test_mock_connection(self) -> None:
        mock_connection = MockFoundationDBConnection()
        mock_dir = mock_connection.directory.create_or_open(('test', 'path'))
        self.assertEqual(mock_dir.path, ('test', 'path'))
        mock_dir[b'test'] = b'test'
        self.assertEqual(mock_dir[b'test'], b'test')
        del mock_dir[b'test']
        self.assertEqual(mock_dir[b'test'], None)
        packed = mock_dir.pack(('test', 'tuple'))
        self.assertEqual(packed, b'\x00\x00\x02test\x00\x02tuple\x00')
        unpacked = mock_dir.unpack(packed)
        self.assertEqual(unpacked, ('test', 'tuple'))

class StructureTestCase(unittest.TestCase):

    def test_validation_directory(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class InvalidDirectoryTestStructure(gateaux.Structure):
            directory = ('test', b'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            InvalidDirectoryTestStructure(mock_connection)
        class NoDirectoryTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            NoDirectoryTestStructure(mock_connection)
        class EmptyDirectoryTestStructure(gateaux.Structure):
            directory = ()
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
             EmptyDirectoryTestStructure(mock_connection)
        class ValidDirectoryTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        ValidDirectoryTestStructure(mock_connection)

    def test_validation_key(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class InvalidKeyTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(), object())
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            InvalidKeyTestStructure(mock_connection)
        class NoKeyTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            NoKeyTestStructure(mock_connection)
        class EmptyKeyTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = ()
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            EmptyKeyTestStructure(mock_connection)
        class ValidKeyTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        ValidKeyTestStructure(mock_connection)

    def test_validation_value(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class InvalidValueTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(), object())
        with self.assertRaises(gateaux.errors.StructureError):
            InvalidValueTestStructure(mock_connection)
        class NoValueTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.StructureError):
            NoValueTestStructure(mock_connection)
        class EmptyValueTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = ()
        with self.assertRaises(gateaux.errors.StructureError):
            EmptyValueTestStructure(mock_connection)
        class ValidValueTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        ValidValueTestStructure(mock_connection)

    def test_pack(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class ValidTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        test = ValidTestStructure(mock_connection)
        with self.assertRaises(gateaux.errors.ValidationError):
            # Too many
            test._pack(test.key, (b'a', b'b', b'c'))
        with self.assertRaises(gateaux.errors.ValidationError):
            # Wrong type
            test._pack(test.key, (b'a', 1))
        packed = test._pack(test.key, (b'a', b'b'))
        self.assertEqual(packed, b'\x00\x00\x01a\x00\x01b\x00')

    def test_unpack(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class ValidTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(), gateaux.BinaryField())
            value = (gateaux.BinaryField(), gateaux.BinaryField())
        test = ValidTestStructure(mock_connection)
        with self.assertRaises(gateaux.errors.ValidationError):
            # Too many
            test._unpack(test.key, b'\x00\x00\x01a\x00\x01b\x00\x01c\x00')
        with self.assertRaises(gateaux.errors.ValidationError):
            # Wrong type
            test._unpack(test.key, b'\x00\x00\x01a\x00\x02b\x00')
        unpacked = test._unpack(test.key, b'\x00\x00\x01a\x00\x01b\x00')
        self.assertEqual(unpacked, (b'a', b'b'))

    def test_interface(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class ValidTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(), gateaux.BinaryField(),)
            value = (gateaux.BinaryField(), gateaux.BinaryField(),)
        test = ValidTestStructure(mock_connection)
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
        mock_connection = MockFoundationDBConnection()
        class ValidTestStructure(gateaux.Structure):
            '''test doc string'''
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        test = ValidTestStructure(mock_connection)
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
