from typing import Type, Union
from .base import BaseField
from ..errors import FieldError, ValidationError


class StringField(BaseField):
    '''
        A StringField() takes and returns strings and stores them as strings. It
        performs no conversion replying on fdb to pack them into bytes.
    '''

    data_type: Type = str

    def __init__(self, max_length: Union[None, int] = None, **kwargs) -> None:
        self.max_length: Union[None, int] = max_length
        super().__init__(**kwargs)

    def pack(self, v: str) -> str:
        '''
            No packing is required. Perform basic validation and return.
        '''
        v = self.validate_packed(v)
        if self.max_length and len(v) > self.max_length:
            raise ValidationError(f'string length of {len(v)} exceeds max_length '
                                  f'of {self.max_length}')
        return v

    def unpack(self, v: str) -> str:
        '''
            No unpacking is required.
        '''
        return self.validate_unpacked(v)
