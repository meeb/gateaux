from typing import Any, Tuple
from .errors import GateauxStructureError
from .fields.base import BaseField


class Structure:

    directory: Tuple = ()
    key: Tuple = ()
    value: Tuple = ()

    def __init__(self, connection:Any=None) -> None:
        if not connection:
            raise GateauxStructureError('fdb connection must be the argument to a '
                                        'structure')
        self.connection = connection
        self.transaction = None
        self.fdb_pack = None
        self.fdb_unpack = None
        fdb_tuple = getattr(self.connection, 'tuple')
        if fdb_tuple:
            self.fdb_pack = getattr(fdb_tuple, 'pack', None)
            self.fdb_unpack = getattr(fdb_tuple, 'unpack', None)
        if not self.fdb_pack or not self.fdb_unpack:
            raise GateauxStructureError('connection has no .tuple.pack or '
                                        '.tuple.unpack methods, is it a fdb '
                                        'connection?')
        self.validate()

    def __getitem__(self, key:Tuple[Any]) -> Tuple:
        print('getitem', key)
        return ()

    def __setitem__(self, key:Tuple[Any], value:Tuple[Any]) -> bool:
        print('setitem', key, value)
        return True

    def __delitem__(self, key:Tuple[Any]) -> bool:
        print('del', key)
        return True

    def validate(self) -> bool:
        '''
            Performs self-validation on a Structure such as validating required
            attributes are set and fields combinations are possible.

            self.directory must be a tuple of strings
            self.key must be a tuple of gateaux Fields
            self.value must be a tuple of gateaux Fields

            Fields can be optional, but optional fields must be at the end of the tuple:
            key = (Field(), Field(), Field(optional=True)) is fine, but
            key = (Field(), Field(optional=True), Field()) is not
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
        found_optional = False
        for i, field in enumerate(self.key):
            if not isinstance(field, BaseField):
                err = f'{me}.key[{i}] is not a field, got: {type(field)}'
                raise GateauxStructureError(err)
            if field.optional:
                found_optional = True
            else:
                if found_optional:
                    err = (f'{me}.key[{i}] is has optional=False, but follows an '
                            'optional field (optional fields can only go at the end '
                            'of the tuple)')
                    raise GateauxStructureError(err)
        # Check the value is valid
        if not isinstance(self.value, tuple):
            raise GateauxStructureError(f'{me}.value must be a tuple')
        if not self.value:
            raise GateauxStructureError(f'{me}.value must not be empty')
        found_optional = False
        for i, field in enumerate(self.value):
            if not isinstance(field, BaseField):
                err = f'{me}.value[{i}] is not a field, got: {type(field)}'
                raise GateauxStructureError(err)
            if field.optional:
                found_optional = True
            else:
                if found_optional:
                    err = (f'{me}.value[{i}] is has optional=False, but follows an '
                            'optional field (optional fields can only go at the end '
                            'of the tuple)')
                    raise GateauxStructureError(err)
        # If we reach here, all looks good
        return True
