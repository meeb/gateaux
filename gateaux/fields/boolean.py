from typing import Type, Union
from .base import BaseField
from ..errors import ValidationError


class BooleanField(BaseField):
    '''
        A BooleanField() takes and returns boolean data as booleans. It performs no
        conversion replying on fdb to pack them into bytes.
    '''

    data_type: Type = bool

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pack(self, v: bool) -> bool:
        '''
            No packing is required.
        '''
        return self.validate_packed(v)

    def unpack(self, v: bool) -> bool:
        '''
            No unpacking is required.
        '''
        return self.validate_unpacked(v)
