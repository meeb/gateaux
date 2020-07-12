from typing import Any, Tuple, List, Dict
from .errors import StructureError, ValidationError
from .fields.base import BaseField


class Structure:

    key: Tuple = ()
    value: Tuple = ()

    def __init__(self, subspace: Any = None) -> None:
        self.key_fields_have_name: bool = True
        self.value_fields_have_name: bool = True
        self.key_field_names: List = []
        self.value_field_names: List = []
        self.validate()
        try:
            if not callable(getattr(subspace, 'pack', None)):
                raise StructureError('provided subspace must have a pack() method')
        except AttributeError:
            raise StructureError('provided subspace must have a pack() method')
        try:
            if not callable(getattr(subspace, 'unpack')):
                raise StructureError('provided subspace must have a unpack() method')
        except AttributeError:
            raise StructureError('provided subspace must have a unpack() method')
        self.subspace: Any = subspace
        self.num_key_fields = len(self.key)
        self.num_value_fields = len(self.value)

    def validate(self) -> bool:
        '''
            Performs self-validation on a Structure such as validating required
            attributes are set:
                * self.key must be a tuple of gateaux Fields
                * self.value must be an empty tuple or a tuple of gateaux Fields
        '''
        me = self.__class__.__name__
        # Check the key is valid
        if not isinstance(self.key, tuple):
            raise StructureError(f'{me}.key must be a tuple')
        if not self.key:
            raise StructureError(f'{me}.key must not be empty')
        for i, field in enumerate(self.key):
            if not isinstance(field, BaseField):
                raise StructureError(f'{me}.key[{i}] is not a field, '
                                     f'got: {type(field)}')
            if field.name:
                self.key_field_names.append(field.name)
            else:
                self.key_fields_have_name = False
        # Check the value is valid
        if not isinstance(self.value, tuple):
            raise StructureError(f'{me}.value must be a tuple')
        for i, field in enumerate(self.value):
            if not isinstance(field, BaseField):
                raise StructureError(f'{me}.value[{i}] is not a field, '
                                     f'got: {type(field)}')
            if field.name:
                self.value_field_names.append(field.name)
            else:
                self.value_fields_have_name = False
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
        return self.subspace.pack(tuple(field_packed))

    def _unpack(self, fields:Tuple, data_bytes: bytes) -> Tuple:
        '''
            Unpacks data_bytes with fdb.tuple.unpack() in the directory subspace then
            passes each value through the .unpack methods of its matching field. Returns
            a tuple of data.
        '''
        if not isinstance(data_bytes, bytes):
            raise ValidationError(f'can only _unpack() bytes, got: {type(data_bytes)}')
        data_tuple = self.subspace.unpack(data_bytes)
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

    def pack_key_dict(self, key_dict: Dict) -> bytes:
        '''
            Pack a directory using the names set for each key field. Internally this
            maps the dict into a tuple using the key field names then passes it to the
            standard pack_key() method.
        '''
        if not self.key_fields_have_name:
            raise StructureError('All key fields must have a "name" set to use '
                                 'pack_key_dict()')
        if not isinstance(key_dict, dict):
            raise ValidationError(f'pack_key_dict(...) must be passed a dict, '
                                  f'got: {type(key_dict)}')
        for k in key_dict.keys():
            if k not in self.key_field_names:
                raise ValidationError(f'Unknown key in dict: {k}')
        keys = []
        for name in self.key_field_names:
            if name not in key_dict:
                break
            keys.append(key_dict[name])
        return self.pack_key(tuple(keys))

    def pack_value_dict(self, value_dict: Dict) -> bytes:
        '''
            Pack a directory using the names set for each value field. Internally this
            maps the dict into a tuple using the value field names then passes it to the
            standard pack_value() method.
        '''
        if not self.value_fields_have_name:
            raise StructureError('All value fields must have a "name" set to use '
                                 'pack_value_dict()')
        if not isinstance(value_dict, dict):
            raise ValidationError(f'pack_value_dict(...) must be passed a dict, '
                                  f'got: {type(value_dict)}')
        for k in value_dict.keys():
            if k not in self.value_field_names:
                raise ValidationError(f'Unknown key in dict: {k}')
        values = []
        for name in self.value_field_names:
            values.append(value_dict.get(name, None))
        return self.pack_value(tuple(values))

    def unpack_key_dict(self, key_bytes: bytes) -> Dict:
        '''
            Unpacks bytes into a tuple, then maps the tuple to the field names into a
            dict.
        '''
        if not self.key_fields_have_name:
            raise StructureError('All key fields must have a "name" set to use '
                                 'unpack_key_dict()')
        key_tuple = self.unpack_key(key_bytes)
        keys = {}
        for i, v in enumerate(key_tuple):
            keys[self.key[i].name] = v
        return keys

    def unpack_value_dict(self, value_bytes: bytes) -> Dict:
        '''
            Unpacks bytes into a tuple, then maps the tuple to the field names into a
            dict.
        '''
        if not self.value_fields_have_name:
            raise StructureError('All key fields must have a "name" set to use '
                                 'unpack_value_dict()')
        key_tuple = self.unpack_value(value_bytes)
        values = {}
        for i, v in enumerate(key_tuple):
            values[self.value[i].name] = v
        return values
