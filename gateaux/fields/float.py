from typing import Type, Union
from .base import BaseField
from ..errors import FieldError, ValidationError


class FloatField(BaseField):
    '''
        A FloatField() takes and returns floats and stores them as floats. It
        performs no conversion replying on fdb to pack them into bytes.
    '''

    data_type: Type = float

    def __init__(self, min_value: Union[None, int] = None,
                 max_value: Union[None, int] = None, **kwargs) -> None:
        if min_value and max_value and min_value >= max_value:
            raise FieldError(f'min_value of {min_value} cannot be greater than or '
                             f'equal to the the max_value of {max_value}')
        self.min_value: Union[None, int] = min_value
        self.max_value: Union[None, int] = max_value
        super().__init__(**kwargs)

    def pack(self, v: float) -> float:
        '''
            No packing is required. Perform basic validation and return.
        '''
        v = self.validate_packed(v)
        if self.min_value and v < self.min_value:
            raise ValidationError(f'value {v} less than min_value of {self.min_value}')
        if self.max_value and v > self.max_value:
            raise ValidationError(f'value {v} greater than max_value of '
                                  f'{self.max_value}')
        return v

    def unpack(self, v: float) -> float:
        '''
            No unpacking is required.
        '''
        return self.validate_unpacked(v)
