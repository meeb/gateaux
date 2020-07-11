# UNDER ACTIVE DEVELOPMENT, DO NOT USE, NOT ON PYPI

# gateaux

Data structures and typing for FoundationDB.

"FoundationDB is a distributed database designed to handle large volumes of structured
data across clusters of commodity servers. It organizes data as an ordered key-value
store and employs ACID transactions for all operations." - taken from
https://github.com/apple/foundationdb/

FoundationDB has, by design, a bare minimum of features. It presents an interface to
applications which reads and writes binary data with a few basic helper layers. 

It has no support for rich data types (for example `datetime` objects) nor provides any
extended data validation. FoundationDB is designed to have layers of abstraction built
on top of it to provide additional features.

`gateaux` is a pure Python 3 (>=3.6) library which provides rich data type handling and
validation on top of the usual `pack()` and `unpack()` methods and extends the
`fdb.tuple` built-in layer. It is loosely modled from the interfaces to relational
database object-relational mapper (RDBMS ORM) systems. Each `gateaux` structure
(comparable to a "model" in the ORM world) effectively formats one single key/value pair
at a time with more rigid validation than the `fdb` library provides out of the box.

`gateaux` does not handle FoundationDB connections for you, just the data parsing
part of your application. Effectively `gateaux` is just a data schema enforcing fancy
wrapper that sits on top of tuple packing and unpacking with some nice syntaxic sugar.
`gateaux` does not abstract away any of the useful existing keyspace interface.

While there is overhead in checking data and converting it between types, `gateaux` is
relatively performant as all it does is shuffle native Python data types about.


## Installation

`gateaux` itself only depends on `foundationdb` and `pytz`. You first need to install
the FoundationDB client libraries from:

https://www.foundationdb.org/download

and FoundationDB Python library from PyPI:

```bash
$ pip install foundationdb
```

Next, install `gateaux` from PyPI:

```bash
$ pip install gateaux
```

Python >= 3.6 is required due to the use of typing.


## Example

```python
from datetime import datetime, timedelta
import fdb
import gateaux

# Connect to your FoundationDB cluster
fdb.api_version(510)
db = fdb.open()


# Define a data structure, an example event log in this case
class EventLog(gateaux.Structure):

    # Every data structure needs a directory as a tuple, this is a FoundationDB
    # directory layer path
    directory = ('log', 'events')

    # Enum members used in the value[1] field
    TYPE_UPLOAD = 0
    TYPE_DOWNLOAD = 1
    TYPE_MEMBERS = (
        TYPE_UPLOAD,
        TYPE_DOWNLOAD,
    )

    # Keys are a tuple of fields
    key = (
        gateaux.DateTimeField(
            name='date',
            help_text='Date and time of the event',
        ),
        gateaux.IPv4Field(
            name='ip address',
            help_text='IPv4 address of the client that triggered the event',
        )
    )

    # Values are also a tuple of fields
    value = (
        gateaux.IntegerField(
            name='bytes'
            min_value=0,
            help_text='Bytes transferred during the event',
        ),
        gateaux.EnumField(
            name='event type',
            members=TYPE_MEMBERS,
            help_text='Type of the event',
        )
    )


# All actions need to be in a transaction, first create an instance of our structure.
# The FoundationDB connection passed here is used solely to open the specified
# FoundationDB directory
event_log = EventLog(db)


# Use the structure
@fdb.transactional
def store_event(tr, ipv4, num_bytes, event_type):
    key = event_log.pack_key(tr, (datetime.now(), ipv4))
    value = event_log.pack_value(tr, (num_bytes, event_type))
    tr[key] = value

store_event(db, '127.0.0.1', 12345, EventLog.TYPE_UPLOAD))


# All available methods at once
@fdb.transactional
def complete_example(tr):
    key_tuple = (datetime.now(), '127.0.0.1')
    value_tuple = (12345, EventLog.TYPE_UPLOAD)
    # Packing
    packed_key = event_log.pack_key(tr, key_tuple)
    packed_value = event_log.pack_value(tr, value_tuple)
    # Unpacking
    unpacked_key = event_log.unpack_key(tr, packed_key)
    unpacked_value = event_log.unpack_value(tr, packed_value)
    # After packing and unpacking they are the same
    assert(key_tuple == unpacked_key)
    assert(value_tuple == unpacked_value)

complete_example(db)


# Exception handling
@fdb.transactional
def complete_example(tr):
    try:
        # Attempting to put a string into a DateTime field
        key_tuple = ('wrong type', '127.0.0.1')
    except gateaux.errors.GateauxValidationError as e:
        # ... handle the error
        print('validation error', e)

```

## Example 2

The FoundationDB example here:
https://apple.github.io/foundationdb/data-modeling.html#data-modeling-tuples
Converted into using `gateaux` structures:

```python
class TemperatureReading(gateaux.Structure):

    directory = ('readings', 'temperatures')

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
        )
    )


temp_reading = TemperatureReading(db)


@fdb.transactional
def set_temp(tr, year, day, degrees):
    key = temp_reading.pack_key((year, day))
    value = temp_reading.pack_value((degrees,))
    tr[key] = value

@fdb.transactional
def get_temp(tr, year, day):
    key = temp_reading.pack_key((year, day))
    return tr[key]
```


## Enforced data format

`gateaux` enforces certain requirements. These are not suitable for every project so
check carefully and verify the libray is appropriate for your application before you
use it:

1. All structures are in their own FoundationDB directory using the directory layer
2. Key tuple members are varialble, a key of 3 elements can contain 1, 2 or 3 values,
   this is to support prefixes and ranges for keys
3. Value tuple members are fixed, a value of 3 elements must always contain 3 values
3. Validation is strict, if you define a field as a StringField you cannot store bytes
   in it etc. Types must match
4. All calls to `gateaux` methods are expected to be made within a FoundationDB
   transaciton, with the transaction as the first argument
5. While possible to support multiple data types, such as cast int(1) to str('1') if an
   integer is provided to a StringField, by choice typing is enforced and this will
   raise an exception
6. You should not use direct binary data with FoundationDB while using `gateaux`, always
   use tuples of other types

`gateaux` conforms to the same idea of `fdb.tuple` such that packing then unpacking a
tuple should always result in the same original tuple of data.


## Structures

There is only one base structure which is inherited to create your own structures.
Synopsis:

```python
import fdb
import gateaux

fdb.api_version(510)
db = fdb.open()

class SomeUserStructure(gateaux.Structure):
    directory = ('some', 'directory')
    key = (
        gateaux.BinaryField(),
    )
    value = (
        gateaux.BinaryField(),
    )

some_structure_instance = SomeUserStructure(db)
```

Structures have one required argument, the FoundationDB connection. Structure instances
have the following interface:

* `structure.pack_key(tr, (...))` validates a tuple of data against the defined key
  fields and returns bytes. The bytes are a FoundationDB packed tuple in the defined
  directory.
* `structure.unpack_key(tr, b'...')` unpacks FoundationDB bytes into a tuple and then
  validates the data against the defined key fields returning the appropriate data type
  for the field.
* `structure.pack_value(tr, (...))` validates a tuple of data against the defined value
  fields and returns bytes. The bytes are a FoundationDB packed tuple in the defined
  directory.
* `structure.unpack_value(tr, b'...')` unpacks FoundationDB bytes into a tuple and then
  validates the data against the defined value fields returning the appropriate data
  type for the field.
* `structure.description` a property which returns a `dict` describing the model,
  including the name of the structure and any doc string as well as lists of
  descriptions for each field in the key and value. You can use this to programatically
  inspect a structure in the future and is useful if you have many structures.

All packing and unpacking methods require a FoundationDB transaction as the first
argument, denoted as `tr` above.


## Fields

All fields support the following arguments:

* `name=string` If set it defines a name stored for the field.

* `help_text=string` If set, help defines some optional help text to describe the data
   stored in the value.

* `null=boolean` If set to True then the field can have a `None` value. Defaults to
   False.

* `default=value` If set, defines a default for a field. The type must match the
  required type for the field.

Other field types may support more arguments.


### `BinaryField`

Stores bytes. Optional arguments:

* `max_length=int` If set defines the maximum number of bytes the field will store.

Accepted type: `bytes`


### `IntegerField` (todo)

Stores integers. Optional arguments:

* `min_value=int` If set defines the minimum number the field will accept
* `max_value=int` If set defines the maximum number the field will accept

Accepted type: `int`


### FloatField (todo)

Stores floats. Optional arguments:

* `min_value=float` If set defines the minimum number the field will accept
* `max_value=float` If set defines the maximum number the field will accept

Accepted type: `float`


### BooleanField (todo)

Stores booleans.

Accepted types: `bool`


### StringField (todo)

Stores strings. Optional arguments:

* `max_length=int` If set defines the maximum length of the field will accept

Accepted type: `str`


### DateTimeField (todo)

Stores datetime instances. Internally stored as a UNIX timestamp and stored in UTC.

Accepted type: `datetime.datetime`


### IPv4AddressField (todo)

Stores IPv4 addresses. Internally stored as 4 bytes.

Accepted types: `ipaddress.IPv4Address`


### IPv4NetworkField (todo)

Stores IPv4 networks. Internally stored as 5 bytes (address + prefix length).

Accepted types: `ipaddress.IPv4Network`


### IPv6AddressField (todo)

Stores IPv6 addresses. Internally stored as 16 bytes.

Accepted types: `ipaddress.IPv6Address`


### IPv6NetworkField (todo)

Stores IPv4 networks. Internally stored as 17 bytes (address + prefix length).

Accepted types: `ipaddress.IPv6Network`


### EnumField (todo)

Stores enums. Internally stored as an integer that maps to a specified value. Required
arguments:

* `members=tuple` A mandatory tuple of tuples of values for the enum.

Example:

```python
MEMBER_A = 0
MEMBER_B = 1
MEMBERS = (
    MEMBER_A,
    MEMBER_B
)
EnumField(members=MEMBERS)
```

Accepted type: `tuple[ints]`


### UUIDField (todo)

Stores UUID instances. Internally stored as 16 bytes.

Accepted types: `uuid.UUID`


## Tests

There is a pretty comprehensive test suite. As `gateaux` is designed to pack and unpack
important data it has good coverage to make sure it's behaving as expected. You can run
it by cloing this repository then execuiting:

```bash
$ ./run-tests.sh
```

The tests perform type checking and require "mypy" from http://mypy-lang.org/ to be
globally installed. E.g. `apt install mypy`.


## Contributing

All properly formatted and sensible pull requests, issues and comments are welcome.
