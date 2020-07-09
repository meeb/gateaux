from typing import Any, Tuple


class Structure:

    directory: Tuple['str']
    key: Tuple
    value: Tuple

    def __init__(self, connection:Any=None) -> None:
        self.connection = connection
        self.fdb_pack = None
        self.fdb_unpack = None
        self.validate()

    def validate(self) -> bool:
        '''
            Performs self-validation on a Structure such as validating required
            attributes are set and fields combinations are possible.
        '''
        return True
