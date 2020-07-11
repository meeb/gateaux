from typing import Type, Union
from .base import BaseField
from ..errors import ValidationError


class BinaryField(BaseField):
    '''
        A BinaryField() takes and returns binary data as bytes. It performs no
        conversion and is the most basic field type. Storage in FoundationDB is also
        as bytes.
    '''

    data_type: Type = bytes

    def __init__(self, max_length: Union[None, int] = None, **kwargs) -> None:
        self.max_length: Union[None, int] = max_length
        super().__init__(**kwargs)

    def pack(self, v: bytes) -> bytes:
        '''
            No packing is required. Perform basic validation and return.
        '''
        if not isinstance(v, self.data_type):
            raise ValidationError(f'pack() expected a value with type '
                                  f'{self.data_type}, got {type(v)}')
        if self.max_length and len(v) > self.max_length:
            raise ValidationError(f'byte length of {len(v)} exceeds max_length '
                                  f'of {self.max_length}')
        return v

    def unpack(self, v: bytes) -> bytes:
        '''
            No unpacking is required. Perform basic validation and return.
        '''
        if not isinstance(v, self.data_type):
            raise ValidationError(f'unpacl() expected a value with type '
                                  f'{self.data_type}, got {type(v)}')
        return v
