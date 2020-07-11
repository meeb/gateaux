from typing import Tuple
import unittest
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


class MockConnectionTestCase(unittest.TestCase):

    def test_mock_connection(self) -> None:
        mock_connection = MockFoundationDBConnection()
        mock_dir = mock_connection.directory.create_or_open(('test', 'path'))
        self.assertEqual(mock_dir.path, ('test', 'path'))
        mock_dir[b'test'] = b'test'
        self.assertEqual(mock_dir[b'test'], b'test')
        del mock_dir[b'test']
        self.assertEqual(mock_dir[b'test'], None)


class StructureTestCase(unittest.TestCase):

    def test_validation_directory(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class InvalidDirectoryTestStructure(gateaux.Structure):
            directory = ('test', b'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.GateauxStructureError):
            InvalidDirectoryTestStructure(mock_connection)
        class NoDirectoryTestStructure(gateaux.Structure):
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.GateauxStructureError):
            NoDirectoryTestStructure(mock_connection)
        class EmptyDirectoryTestStructure(gateaux.Structure):
            directory = ()
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.GateauxStructureError):
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
        with self.assertRaises(gateaux.errors.GateauxStructureError):
            InvalidKeyTestStructure(mock_connection)
        class NoKeyTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.GateauxStructureError):
            NoKeyTestStructure(mock_connection)
        class EmptyKeyTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = ()
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.GateauxStructureError):
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
        with self.assertRaises(gateaux.errors.GateauxStructureError):
            InvalidValueTestStructure(mock_connection)
        class NoValueTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            value = (gateaux.BinaryField(),)
        with self.assertRaises(gateaux.errors.GateauxStructureError):
            NoValueTestStructure(mock_connection)
        class EmptyValueTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = ()
        with self.assertRaises(gateaux.errors.GateauxStructureError):
            EmptyValueTestStructure(mock_connection)
        class ValidValueTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        ValidValueTestStructure(mock_connection)

    def test_interface(self) -> None:
        mock_connection = MockFoundationDBConnection()
        class ValidTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)
        test = ValidTestStructure(mock_connection)
        # TODO: rest of test

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
        # Field description testing is performed in test_field_base, no need to dupe
        self.assertIsInstance(desc['key'], list)
        self.assertEqual(len(desc['key']), 1)
        self.assertIsInstance(desc['key'][0], dict)
        self.assertIsInstance(desc['value'], list)
        self.assertEqual(len(desc['value']), 1)
        self.assertIsInstance(desc['value'][0], dict)
