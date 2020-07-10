from typing import Any, Tuple


class BaseField:
    '''
        Describes a basic interface that fields must implement.
    '''

    # The data type which is accepted as an input and returned as an output
    data_type: Any = object

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
        if 'null' in kwargs:
            self.null = kwargs['null']
            if not isinstance(self.null, bool):
                raise TypeError('"null" must be a bool')
            del kwargs['null']
        else:
            self.null = False
        if 'default' in kwargs:
            self.default = kwargs['default']
            if not isinstance(self.default, self.data_type):
                raise TypeError('"default" must be a {type(self.data_type)}')
            del kwargs['default']
        else:
            self.default = None
        if kwargs:
            err = 'Unexpected keyword arguments passed to field: {}'
            raise ValueError(err.format(kwargs.keys()))

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
