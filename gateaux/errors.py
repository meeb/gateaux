class GateauxError(Exception):
    '''
        Base for all other gateaux exceptions
    '''
    pass


class StructureError(GateauxError):
    '''
        Raised when there is an error in the construct of a Structure, such as invalid
        fields or no directory path.
    '''
    pass


class ValidationError(GateauxError):
    '''
        Raised for data validation errors, such as attempting to store a str in an
        IntegerField.
    '''
    pass
