from typing import Any, Tuple
from .errors import GateauxStructureError
from .fields.base import BaseField


class Structure:

    directory: Tuple = ()
    key: Tuple = ()
    value: Tuple = ()

    def __init__(self, connection:Any) -> None:
        self.connection:Any = connection
        self.validate()
        self.fdbdir:Any = self.connection.directory.create_or_open(self.directory)

    def validate(self) -> bool:
        '''
            Performs self-validation on a Structure such as validating required
            attributes are set:
                * self.directory must be a tuple of strings
                * self.key must be a tuple of gateaux Fields
                * self.value must be a tuple of gateaux Fields
        '''
        me = self.__class__.__name__
        # Validate the directory attribute
        if not isinstance(self.directory, tuple):
            raise GateauxStructureError(f'{me}.directory must be a tuple')
        if not self.directory:
            raise GateauxStructureError(f'{me}.directory must not be empty')
        for i, dir_part in enumerate(self.directory):
            if not isinstance(dir_part, str):
                err = f'{me}.directory[{i}] is not a string, got: {type(dir_part)}'
                raise GateauxStructureError(err)
        # Check the key is valid
        if not isinstance(self.key, tuple):
            raise GateauxStructureError(f'{me}.key must be a tuple')
        if not self.key:
            raise GateauxStructureError(f'{me}.key must not be empty')
        for i, field in enumerate(self.key):
            if not isinstance(field, BaseField):
                err = f'{me}.key[{i}] is not a field, got: {type(field)}'
                raise GateauxStructureError(err)
        # Check the value is valid
        if not isinstance(self.value, tuple):
            raise GateauxStructureError(f'{me}.value must be a tuple')
        if not self.value:
            raise GateauxStructureError(f'{me}.value must not be empty')
        for i, field in enumerate(self.value):
            if not isinstance(field, BaseField):
                err = f'{me}.value[{i}] is not a field, got: {type(field)}'
                raise GateauxStructureError(err)
        # If we reach here, all looks good
        return True

    def describe(self) -> dict:
        return {}

    def _pack(self, tr:Any, data_tuple: Tuple) -> bytes:
        return b''

    def _unpack(self, tr:Any, bytes: bytes) -> Tuple:
        return ()

    def pack_key(self, tr:Any, key_tuple: Tuple) -> bytes:
        return b''

    def pack_value(self, tr:Any, value_tuple: Tuple) -> bytes:
        return b''

    def unpack_key(self, tr:Any, key_bytes: bytes) -> Tuple:
        return ()

    def unpack_value(self, tr:Any, value_bytes: bytes) -> Tuple:
        return ()
