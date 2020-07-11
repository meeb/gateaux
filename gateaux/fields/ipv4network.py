from typing import Type
from ipaddress import IPv4Network
from .base import BaseField
from ..errors import ValidationError


class IPv4NetworkField(BaseField):
    '''
        A IPv4NetworkField() takes and returns ipaddress.IPv4Network instances data as
        bytes. It performs ipaddress.IPv4Network to bytes conversion. Internally,
        these are stored as 5 bytes. The first 4 bytes are the packed IP address and the
        last byte is the prefix length.
    '''

    data_type: Type = IPv4Network

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pack(self, v: IPv4Network) -> bytes:
        '''
            Pack an IPv4Network into bytes.
        '''
        v = self.validate_packed(v)
        network: IPv4Network = IPv4Network(v)
        return network.network_address.packed + bytes([network.prefixlen])

    def unpack(self, v: bytes) -> IPv4Network:
        '''
            Unpack bytes into an IPv4Network.
        '''
        if not isinstance(v, bytes):
            raise ValidationError(f'unpack() expected bytes, got: {type(v)}')
        if len(v) != 5:
            raise ValidationError(f'unpack() expected exactly 5 bytes, got: {len(v)}')
        network: IPv4Network = IPv4Network((v[0:4], v[4]))
        return self.validate_unpacked(network)
