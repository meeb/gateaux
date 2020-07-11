from typing import Type
from ipaddress import IPv6Address
from .base import BaseField
from ..errors import ValidationError


class IPv6AddressField(BaseField):
    '''
        A IPv6AddressField() takes and returns ipaddress.IPv6Address instances data as
        bytes. It performs ipaddress.IPv6Address to bytes conversion.
    '''

    data_type: Type = IPv6Address

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pack(self, v: IPv6Address) -> bytes:
        '''
            Pack an IPv6Address into bytes.
        '''
        v = self.validate_packed(v)
        ip: IPv6Address = IPv6Address(v)
        return ip.packed

    def unpack(self, v: bytes) -> IPv6Address:
        '''
            Unpack bytes into an IPv6Address.
        '''
        if not isinstance(v, bytes):
            raise ValidationError(f'unpack() expected bytes, got: {type(v)}')
        ip: IPv6Address = IPv6Address(v)
        return self.validate_unpacked(ip)
