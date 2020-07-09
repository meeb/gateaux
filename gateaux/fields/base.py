from typing import Any


class BaseField:
    '''
        Describes a basic interface that fields must implement.
    '''

    def __init__(self, **kwargs) -> None:
        if 'name' in kwargs:
            self.name = kwargs['name']
            if not isinstance(self.name, str):
                raise TypeError('"name" must be a str')
            del kwargs['name']
        else:
            self.name = ''
        if 'help_text' in kwargs:
            self.help_text = kwargs['help_text']
            if not isinstance(self.help_text, str):
                raise TypeError('"help_text" must be a str')
            del kwargs['help_text']
        else:
            self.help_text = ''
        if 'optional' in kwargs:
            self.optional = kwargs['optional']
            if not isinstance(self.optional, bool):
                raise TypeError('"optional" must be a bool')
            del kwargs['optional']
        else:
            self.optional = False
        if kwargs:
            err = 'Unexpected keyword arguments passed to field: {}'
            raise ValueError(err.format(kwargs.keys()))

    def validate(self, v:Any) -> bool:
        '''
            If implemented, validate() performs prepacking validation on the value.
        '''
        raise NotImplementedError('validate() must be implemented if called')

    def pack(self, v:Any):
        '''
            A field pack accepts one or more types and returns only one type. The
            return of pack() must be one of integer, string or bytes to be pack()'d
            by FoundationDB's client.
        '''
        raise NotImplementedError('pack() must be defined')

    def unpack(self, v:Any):
        '''
            An unpack accepts one data type and returns it or converts it to another
            type. The input to unpack() must be one of integer, string or bytes and
            the result must be a standard type, like integer or datetime().
        '''
        raise NotImplementedError('unpack() must be defined')
