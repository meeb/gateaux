from .base import BaseField
from ..errors import GateauxValidationError


class BinaryField(BaseField):
    '''
        A BinaryField() takes and returns binary data as bytes. It performs no
        conversion and is the most basic field type. Storage in FoundationDB is also
        as bytes.
    '''

    def __init__(self, max_length:int=0, **kwargs) -> None:
        self.max_length = max_length
        super().__init__(**kwargs)

    def validate(self, v:bytes) -> bool:
        '''
            Only one type of input is accepted for a BinaryField therefore the only
            validation required is to check the maximum length.
        '''
        if self.max_length > 0:
            if len(v) > self.max_length:
                err = 'byte length of {} exceeds max_length of {}'
                raise GateauxValidationError(err.format(len(v), self.max_length))
        return True

    def pack(self, v:bytes) -> bytes:
        '''
            No packing is required.
        '''
        self.validate(v)
        return v

    def unpack(self, v:bytes) -> bytes:
        '''
            No unpacking is required.
        '''
        return v
