__version__ = 0.1


from .errors import (GateauxError, GateauxStructureError, GateauxValidationError,
                     GateauxPackError, GateaxUnpackError)
from .structure import Structure
from .fields.base import BaseField
from .fields.binary import BinaryField
