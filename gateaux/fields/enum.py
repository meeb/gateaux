from typing import Type, Tuple
from .base import BaseField
from ..errors import FieldError, ValidationError


class EnumField(BaseField):
    '''
        A EnumField() takes and returns numbers and stores them as numbers with extended
        validation to confirm that the integer is in the tuple of provided members. It
        performs no conversion replying on fdb to pack them into bytes.
    '''

    data_type: Type = int

    def __init__(self, members: Tuple[int, ...] = (), **kwargs) -> None:
        if not isinstance(members, tuple):
            raise FieldError(f'members must be a tuple of ints')
        for i, v in enumerate(members):
            if not isinstance(v, int):
                raise FieldError(f'members[{i}] is not an int')
        if not members:
            raise FieldError(f'members must be a tuple of ints and not empty')
        self.members: Tuple[int, ...] = members
        super().__init__(**kwargs)

    def pack(self, v: int) -> int:
        '''
            No packing is required. Confirm the int is in the members.
        '''
        v = self.validate_packed(v)
        if v not in self.members:
            raise ValidationError('{v} is not a valid member int')
        return v

    def unpack(self, v: int) -> int:
        '''
            No unpacking is required.
        '''
        return self.validate_unpacked(v)
