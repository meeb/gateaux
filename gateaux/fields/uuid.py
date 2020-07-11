from typing import Type
from uuid import UUID
from .base import BaseField
from ..errors import ValidationError


class UUIDField(BaseField):
    '''
        A UUIDField() takes and returns uuid.UUID instances as bytes. It performs
        uuid.UUID to bytes conversion.
    '''

    data_type: Type = UUID

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pack(self, v: UUID) -> bytes:
        '''
            Pack a UUID into bytes.
        '''
        v = self.validate_packed(v)
        return v.bytes

    def unpack(self, v: bytes) -> UUID:
        '''
            Unpack bytes into a UUID.
        '''
        if not isinstance(v, bytes):
            raise ValidationError(f'unpack() expected bytes, got: {type(v)}')
        if len(v) != 16:
            raise ValidationError(f'unpack() expected exactly 16 bytes, got: {len(v)}')
        id: UUID = UUID(bytes=v)
        return self.validate_unpacked(id)
