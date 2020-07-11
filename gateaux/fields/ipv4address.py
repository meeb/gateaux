from typing import Type
from ipaddress import IPv4Address
from .base import BaseField
from ..errors import ValidationError


class IPv4AddressField(BaseField):
    '''
        A IPv4AddressField() takes and returns ipaddress.IPv4Address instances data as
        bytes. It performs ipaddress.IPv4Address to bytes conversion.
    '''

    data_type: Type = IPv4Address

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pack(self, v: IPv4Address) -> bytes:
        '''
            Pack an IPv4Address into bytes.
        '''
        v = self.validate_packed(v)
        return v.packed

    def unpack(self, v: bytes) -> IPv4Address:
        '''
            Unpack bytes into an IPv4Address.
        '''
        if not isinstance(v, bytes):
            raise ValidationError(f'unpack() expected bytes, got: {type(v)}')
        if len(v) != 4:
            raise ValidationError(f'unpack() expected exactly 4 bytes, got: {len(v)}')
        ip: IPv4Address = IPv4Address(v)
        return self.validate_unpacked(ip)
