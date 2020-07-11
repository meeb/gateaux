from typing import Tuple, Type
from .base import BaseField
from ..errors import ValidationError


class BinaryField(BaseField):
    '''
        A BinaryField() takes and returns binary data as bytes. It performs no
        conversion and is the most basic field type. Storage in FoundationDB is also
        as bytes.
    '''

    data_type: Type = bytes

    def __init__(self, max_length:int=0, **kwargs) -> None:
        self.max_length: int = max_length
        super().__init__(**kwargs)

    def pack(self, v:bytes) -> bytes:
        '''
            No packing is required. Perform basic validation and return.
        '''
        # Check the arg is of an expected pack data type
        if not isinstance(v, self.data_type):
            err = f'expected one of {self.data_type} types, got {type(v)}'
            raise ValidationError(err)
        if self.max_length > 0:
            if len(v) > self.max_length:
                err = f'byte length of {len(v)} exceeds max_length of {self.max_length}'
                raise ValidationError(err)
        return v

    def unpack(self, v:bytes) -> bytes:
        '''
            No unpacking is required. Perform basic validation and return.
        '''
        # Check the arg is of a valid type
        if not isinstance(v, self.data_type):
            err = f'expected one of {self.data_type} types, got {type(v)}'
            raise ValidationError(err)
        return v
