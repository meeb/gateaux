from typing import Tuple, Type, Union
from .base import BaseField
from ..errors import FieldError, ValidationError


class IntegerField(BaseField):
    '''
        A IntegerField() takes and returns numbers and stores them as numbers. It
        performs no conversion replying on fdb to pack them into bytes.
    '''

    data_type: Type = int

    def __init__(self, min_value: Union[None, int] = None,
                 max_value: Union[None, int] = None, **kwargs) -> None:
        if min_value and max_value and min_value >= max_value:
            raise FieldError(f'min_value of {min_value} cannot be greater than or '
                             f'equal to the the max_value of {max_value}')
        self.min_value: Union[None, int] = min_value
        self.max_value: Union[None, int] = max_value
        super().__init__(**kwargs)

    def pack(self, v: int) -> int:
        '''
            No packing is required. Perform basic validation and return.
        '''
        v = self.validate_packed(v)
        if not isinstance(v, self.data_type):
            raise ValidationError(f'pack() expected a value with type '
                                  f'{self.data_type}, got {type(v)}')
        if self.min_value and v < self.min_value:
            raise ValidationError(f'value {v} less than min_value of {self.min_value}')
        if self.max_value and v > self.max_value:
            raise ValidationError(f'value {v} greater than max_value of '
                                  f'{self.max_value}')
        return v

    def unpack(self, v: int) -> int:
        '''
            No unpacking is required.
        '''
        return self.validate_unpacked(v)
