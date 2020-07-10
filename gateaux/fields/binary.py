from typing import Any, Tuple
from .base import BaseField
from ..errors import GateauxValidationError


class BinaryField(BaseField):
    '''
        A BinaryField() takes and returns binary data as bytes. It performs no
        conversion and is the most basic field type. Storage in FoundationDB is also
        as bytes.
    '''

    pack_types: Tuple = (bytes,)
    unpack_type: Any = bytes

    def __init__(self, max_length:int=0, **kwargs) -> None:
        self.max_length: int = max_length
        super().__init__(**kwargs)

    def pack(self, v:bytes) -> bytes:
        '''
            No packing is required. Perform basic validation and return.
        '''
        # Check the arg is of an expected pack data type
        if not isinstance(v, self.pack_types):
            err = f'expected one of {self.pack_types} types, got {type(v)}'
            raise GateauxValidationError(err)
        if self.max_length > 0:
            if len(v) > self.max_length:
                err = f'byte length of {len(v)} exceeds max_length of {self.max_length}'
                raise GateauxValidationError(err)
        return v

    def unpack(self, v:bytes) -> bytes:
        '''
            No unpacking is required. Perform basic validation and return.
        '''
        # Check the arg is of a valid type
        if not isinstance(v, self.unpack_type):
            err = f'expected one of {self.pack_types} types, got {type(v)}'
            raise GateauxValidationError(err)
        return v
