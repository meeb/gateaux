# UNDER ACTIVE DEVELOPMENT, DO NOT USE

# gateaux

Data structures and typing for FoundationDB.

"FoundationDB is a distributed database designed to handle large volumes of structured
data across clusters of commodity servers. It organizes data as an ordered key-value
store and employs ACID transactions for all operations." - taken from
https://github.com/apple/foundationdb/

FoundationDB has, by design, a bare minimum of features. It presents an interface to
applications which reads and writes binary data. The only structure it provides
natively is `pack()` and `unpack()` which convert tuples of data into binary, and binary
back out into tuples of data. The tuples themselves can contain strings, integers,
floats and bytes.

It has no support for rich data types (for example `datetime` objects) nor provides any
data validation. FoundationDB is designed to have layers of abstraction built on top of
it to provide additional features.

`gateaux` is a pure Python 3 (>=3.6) library which provides automatic rich data type
handling and validation. Logically, it sits somewhere between bare FoundationDB and full
layer implemenations for more complex applications. It is loosely modled from the
interfaces to relational database object-relational mapper (RDBMS ORM) systems. Each
`gateaux` structure (comparable to a "model") effectively formats one single key/value
pair at a time.

`gateaux` does not handle FoundationDB connections for you, just the data parsing
part of your application. Effectively `gateaux` is just a fancy wrapper that sits on top
of `fdb.tuple.pack` and `fdb.tuple.unpack` with some nice syntaxic sugar.

While there is overhead in checking data and converting it between types, `gateaux` is
relatively performant.


## Installation

First, you need to install the FoundationDB client from:

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

    # Every data structure needs a directory as a tuple, this is a FoundationDB dir
    directory = ('log', 'events')

    # Enum members
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


# You can use structure directly with the FoundationDB connection
event_log = EventLog(db)

# And then use an event_log object like you would use the db object
event_log[(datetime.now(), '127.0.0.1')] = (12345, EventLog.TYPE_UPLOAD)

# Or, you can create the structure object without a connection for use in a transaction
event_log = EventLog()

@fdb.transactional
def store_event(tr, ipv4, num_bytes, event_type):
    event_log.connection = tr
    event_log[(datetime.now(), ipv4)] = (num_bytes, event_type)

store_event(db, '127.0.0.1', 12345, EventLog.TYPE_UPLOAD))

# You can fetch values by key
dt = datetime(year=2020, month=7, day=1)
(num_bytes, event_type) = event_log[(dt, '127.0.0.1')]

# And get ranges between keys
from_key = (dt, '127.0.0.1')
to_key = (dt + timedelta(days=1), 127.0.0.1')
for (dt, ipv4), (num_bytes, event_type) in event_log[from_key:to_key]:
    print((dt, ipv4), ' = ', (num_bytes, event_type))

# And delete keys
del event_log[(dt, '127.0.0.1')]

# And delete ranges
del event_log[from_key:to_key]

# If you attempt to pass in any invalid data, such as a string into an IntegerField,
# a gateaux.errors.GateauxValidationError exception will be raised
try:
    event_log[(datetime.now(), '127.0.0.1')] = ('not an integer', EventLog.TYPE_UPLOAD)
except gateaux.errors.GateauxValidationError as e:
    print('validation error:', e)
```


## Structures

There is only one base structure which is inherited to create your own structures.
Synopsis:

```python
import gateaux

class SomeUserStructure(gateaux.Structure):
    directory = ('some', 'directory')
    key = (
        gateaux.BinaryField(),
    )
    value = (
        gateaux.BinaryField(),
    )
```

Structures support the following argument:

* `connection=[foundation db connection]` If set, the FoundationDB connection to use.

You can override the attribute when using `@fdb.transactional` wrapped functions which
allows you to only initialise the structures once then re-use them.

```python
some_data = SomeUserStructure()

@fdb.transactional
def some_function(tr, args):
    some_data.connection = tr
```


## Fields

All fields support the following arguments:

* `name=string` If set it defines a name stored for the field.

* `help_text=string` If set, help defines some optional help text to describe the data
   stored in the value.

* `optional=boolean` If set to True then the field can have a `None` value. Defaults to
   False. Optional fields must be at the end of the tuple. For example:
   `key = (Field(), Field(), Field(optional=True))` is allowed, but
   `key = (Field(), Field(optional=True), Field())` is not. The optional field in the
   middle of the key or value tuple is not permitted.

* `default=value` If set, defines a default for a value. The type must match the
  required type for the field.

### `BinaryField`

Stores bytes. Optional arguments:

* `max_length=Integer` If set defines the maximum number of bytes the field will store.

Accepted input type: `bytes`
Output type: `bytes`

### `IntegerField`

Stores integers. Optional arguments:

* `min=Integer` If set defines the minimum number the value will accept
* `max=Integer` If set defines the maximum number the value will accept

Accepted input type: `int`
Output type: `int`

### FloatField

Stores floats. Optional arguments:

* `min=Integer` If set defines the minimum number the value will accept
* `max=Integer` If set defines the maximum number the value will accept

Accepted input types: `int`, `float`
Output type: `float`

### BooleanField

Stores floats. Optional arguments:

* `min=Integer` If set defines the minimum number the value will accept
* `max=Integer` If set defines the maximum number the value will accept

Accepted input types: `int`, `float`
Output type: `float`

### StringField

Stores strings. Optional arguments:

* `max_length=Integer` If set defines the maximum length of strings to store

Accepted input type: `str`
Output type: `str`

### DateTimeField

Stores datetime instances. Internally stored as a UNIX timestamp and stored in UTC.
Optional arguments:

* `timezone=timezone` If set, defines the `pytz` timezone such as `pytz.UTC` which the
  datetime will be converted to when read.

Accepted input types: `datetime.datetime`, `int`
Output type: `datetime.datetime`

### IPv4AddressField

Stores IPv4 addresses. Internally stored as 4 bytes.

Accepted input types: `ipaddress.IPv4Address`, `str`
Output type: `ipaddress.IPv4Address`

### IPv4NetworkField

Stores IPv4 networks. Internally stored as 5 bytes (address + prefix length).

Accepted input types: `ipaddress.IPv4Network`, `str`
Output type: `ipaddress.IPv4Network`

### IPv6AddressField

Stores IPv6 addresses. Internally stored as 16 bytes.

Accepted input types: `ipaddress.IPv6Address`, `str`
Output type: `ipaddress.IPv6Address`

### IPv6NetworkField

Stores IPv4 networks. Internally stored as 17 bytes (address + prefix length).

Accepted input types: `ipaddress.IPv6Network`, `str`
Output type: `ipaddress.IPv6Network`

### EnumField

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

Accepted input type: `int` (must be an `int` specified in `members` tuple)
Output type: `int`

### UUIDField

Stores UUID instances. Internally stored as 16 bytes.

Accepted input types: `uuid.UUID`, `str`, `int`, `bytes`
Output type: `uuid.UUID`


## Tests

There is a test suite, you can run it by cloing this repository then execuiting:

```bash
$ ./run-tests.sh
```

The tests perform type checking and require "mypy" from http://mypy-lang.org/ to be
globally installed. E.g. `apt install mypy`.


## Contributing

All properly formatted and sensible pull requests, issues and comments are welcome.
