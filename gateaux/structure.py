from typing import Any, Tuple
import fdb
from fdb.impl import Database
from fdb.directory_impl import DirectorySubspace
from .errors import StructureError, ValidationError
from .fields.base import BaseField


class Structure:

    directory: Tuple = ()
    key: Tuple = ()
    value: Tuple = ()

    def __init__(self, connection: Database,
                 directory: DirectorySubspace = None) -> None:
        self.validate()
        self.connection: Database = connection
        if directory:
            self.fdbdir: DirectorySubspace = directory
        else:            
            self.fdbdir: DirectorySubspace = fdb.directory.create_or_open(
                self.connection, self.directory)
        self.num_key_fields = len(self.key)
        self.num_value_fields = len(self.value)

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
            raise StructureError(f'{me}.directory must be a tuple')
        if not self.directory:
            raise StructureError(f'{me}.directory must not be empty')
        for i, dir_part in enumerate(self.directory):
            if not isinstance(dir_part, str):
                raise StructureError(f'{me}.directory[{i}] is not a string, '
                                     f'got: {type(dir_part)}')
        # Check the key is valid
        if not isinstance(self.key, tuple):
            raise StructureError(f'{me}.key must be a tuple')
        if not self.key:
            raise StructureError(f'{me}.key must not be empty')
        for i, field in enumerate(self.key):
            if not isinstance(field, BaseField):
                raise StructureError(f'{me}.key[{i}] is not a field, '
                                     f'got: {type(field)}')
        # Check the value is valid
        if not isinstance(self.value, tuple):
            raise StructureError(f'{me}.value must be a tuple')
        if not self.value:
            raise StructureError(f'{me}.value must not be empty')
        for i, field in enumerate(self.value):
            if not isinstance(field, BaseField):
                raise StructureError(f'{me}.value[{i}] is not a field, '
                                     f'got: {type(field)}')
        # If we reach here, all looks good
        return True

    @property
    def description(self) -> dict:
        desc: dict = {
            'name': self.__class__.__name__,
            'doc': self.__doc__,
            'key': [],
            'value': [],
        }
        for field in self.key:
            desc['key'].append(field.description)
        for field in self.value:
            desc['value'].append(field.description)
        return desc

    def _pack(self, fields:Tuple, data_tuple: Tuple) -> bytes:
        '''
            Passes each value in a data_tuple through the .pack() method of its
            matching field, then returns the resulting tuple through fdb.tuple.pack()
            in the directory subspace as bytes.
        '''
        if len(data_tuple) > len(fields):
            raise ValidationError(f'cannot _pack(), data tuple has {len(data_tuple)} '
                                  f'elements, larger than the number of fields '
                                  f'at {len(fields)}')
        field_packed: list = []
        for i, v in enumerate(data_tuple):
            field_packed.append(fields[i].pack(v))
        return self.fdbdir.pack(tuple(field_packed))

    def _unpack(self, fields:Tuple, data_bytes: bytes) -> Tuple:
        '''
            Unpacks data_bytes with fdb.tuple.unpack() in the directory subspace then
            passes each value through the .unpack methods of its matching field. Returns
            a tuple of data.
        '''
        data_tuple = self.fdbdir.unpack(data_bytes)
        if len(data_tuple) > len(fields):
            raise ValidationError(f'cannot _unpack(), data tuple has {len(data_tuple)} '
                                  f'elements, larger than the number of fields '
                                  f'at {len(fields)}')
        field_unpacked: list = []
        for i, v in enumerate(data_tuple):
            field_unpacked.append(fields[i].unpack(v))
        return tuple(field_unpacked)

    def pack_key(self, key_tuple: Tuple) -> bytes:
        '''
            Keys can be of variable length providing it is > 0 and <= number of defined
            key fields in the structure.
        '''
        if not isinstance(key_tuple, tuple):
            raise ValidationError(f'pack_key(...) must be passed a tuple, '
                                  f'got: {type(key_tuple)}')
        key_len = len(key_tuple)
        if key_len <= 0:
            raise ValidationError(f'key tuple must contain at least 1 value, '
                                  f'got: {key_len}')
        if key_len > self.num_key_fields:
            raise ValidationError(f'key tuple must contain {self.num_key_fields} or '
                                  f'fewer values to match the structures key '
                                  'definitions, got: {key_len}')
        return self._pack(self.key, key_tuple)

    def pack_value(self, value_tuple: Tuple) -> bytes:
        '''
            Values must be of the same length as the number of value fields defined
            in the structure.
        '''
        if len(value_tuple) != self.num_value_fields:
            raise ValidationError(f'value tuple must contain {self.num_value_fields} '
                                  f'values to match the structure, '
                                  f'got: {len(value_tuple)}')
        return self._pack(self.value, value_tuple)

    def unpack_key(self, key_bytes: bytes) -> Tuple:
        '''
            Keys are validated when written, unpack any values providing they are known
            by the defined key fields.
        '''
        return self._unpack(self.key, key_bytes)

    def unpack_value(self, value_bytes: bytes) -> Tuple:
        '''
            Values are validated when written, unpack any values providing they are
            known by the defined value fields.
        '''
        return self._unpack(self.value, value_bytes)
