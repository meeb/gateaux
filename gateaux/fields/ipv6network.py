from typing import Type
from ipaddress import IPv6Network
from .base import BaseField
from ..errors import ValidationError


class IPv6NetworkField(BaseField):
    '''
        A IPv4NetworkField() takes and returns ipaddress.IPv4Network instances data as
        bytes. It performs ipaddress.IPv4Network to bytes conversion. Internally,
        these are stored as 5 bytes. The first 4 bytes are the packed IP address and the
        last byte is the prefix length.
    '''

    data_type: Type = IPv6Network

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pack(self, v: IPv6Network) -> bytes:
        '''
            Pack an IPv4Network into bytes.
        '''
        v = self.validate_packed(v)
        network: IPv6Network = IPv6Network(v)
        return network.network_address.packed + bytes([network.prefixlen])

    def unpack(self, v: bytes) -> IPv6Network:
        '''
            Unpack bytes into an IPv6Network.
        '''
        if not isinstance(v, bytes):
            raise ValidationError(f'unpack() expected bytes, got: {type(v)}')
        if len(v) != 17:
            raise ValidationError(f'unpack() expected exactly 17 bytes, got: {len(v)}')
        network: IPv6Network = IPv6Network((v[0:16], v[16]))
        return self.validate_unpacked(network)
