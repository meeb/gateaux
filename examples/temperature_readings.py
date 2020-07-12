#!/usr/bin/env python3
'''
    The FoundationDB example here:
    https://apple.github.io/foundationdb/data-modeling.html#data-modeling-tuples
    Converted into using `gateaux` structures and some test code added.
'''


import fdb
import gateaux


fdb.api_version(510)



class TemperatureReading(gateaux.Structure):

    key = (
        gateaux.IntegerField(
            name='year',
        ),
        gateaux.IntegerField(
            name='day',
        )
    )

    value = (
        gateaux.IntegerField(
            name='degrees',
        ),
    )


db = fdb.open()
temp_reading_space = fdb.Subspace(('temp_readings',))
temp_reading = TemperatureReading(temp_reading_space)


@fdb.transactional
def clear_space(tr):
    # Clean up
    del tr[temp_reading_space.range()]


@fdb.transactional
def set_temp(tr, year, day, degrees):
    key = temp_reading.pack_key((year, day))
    value = temp_reading.pack_value((degrees,))
    tr[key] = value


@fdb.transactional
def get_temp(tr, year, day):
    key = temp_reading.pack_key((year, day))
    return temp_reading.unpack_value(tr[key])[0]


if __name__ == '__main__':
    import random
    # Clean up
    clear_space(db)
    year = 2020
    # Store a years worth of example readings
    for day in range(1, 366):
        degree = random.randint(10, 35)
        set_temp(db, year, day, degree)
    # Read them back out again
    for day in range(1, 366):
        degrees = get_temp(db, year, day)
        print(f'{year}-{day} = {degrees} degrees')
    # Clean up
    clear_space(db)
