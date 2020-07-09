from typing import Tuple
import unittest
import gateaux


class MockFoundationConnection:
    '''
        Bare-bones emulation of a FoundationDB client connection.
    '''

    def __init__(self):

        class MockTuple:

            def pack(self, v:Tuple) -> bytes:
                return b'mock'

            def unpack(self, v:bytes) -> Tuple:
                return (b'mock',)
        
        self.tuple = MockTuple()

    def __getitem__(self, key:Tuple) -> Tuple:
        print('[mock fdb get]', key)
        return (b'mock',)

    def __setitem__(self, key:Tuple, value:Tuple) -> bool:
        print('[mock fdb set]', key, '=', value)
        return True

    def __delitem__(self, key:Tuple) -> bool:
        print('[mock fdb del]', key)
        return True


class StructureTestCase(unittest.TestCase):

    def test_validation_directory(self) -> None:
        mock_connection = MockFoundationConnection()
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
        mock_connection = MockFoundationConnection()
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
        mock_connection = MockFoundationConnection()
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

    def test_bare_structure(self) -> None:

        class ValidTestStructure(gateaux.Structure):
            directory = ('test', 'directory')
            key = (gateaux.BinaryField(),)
            value = (gateaux.BinaryField(),)

        mock_connection = MockFoundationConnection()
        test = ValidTestStructure(mock_connection)
        self.assertEqual(test.connection, mock_connection)
