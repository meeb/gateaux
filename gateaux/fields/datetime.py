from typing import Type, Union
from datetime import datetime
from calendar import timegm
import pytz
from .base import BaseField
from ..errors import ValidationError


class DateTimeField(BaseField):
    '''
        A DateTimeField() takes and returns datetime.datetime instances data as
        floats. It performs datetime.datetime to floats conversion and relies on
        fdb to pack the floats into bytes.
    '''

    data_type: Type = datetime

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def pack(self, v: datetime) -> float:
        '''
            Normalise the datetime into UTC and convert it to a UNIX timestamp,
            preserving the microseconds.
        '''
        v = self.validate_packed(v)
        unixts:int = timegm(v.timetuple())
        return unixts + (v.microsecond / 100000)

    def unpack(self, v: float) -> datetime:
        '''
            Convert a UNIX timestamp to a datetime in UTC.
        '''
        if not isinstance(v, float):
            raise ValidationError(f'unpack() expected an float, got: {type(v)}')
        dt:datetime = datetime.utcfromtimestamp(v)
        dt = pytz.utc.localize(dt)
        return self.validate_unpacked(dt)
