# gateaux

Data structures and typing for FoundationDB.

"FoundationDB is a distributed database designed to handle large volumes of structured
data across clusters of commodity servers. It organizes data as an ordered key-value
store and employs ACID transactions for all operations." - taken from
https://github.com/apple/foundationdb/

FoundationDB has, by design, a bare minimum of features. It presents an interface to
applications which reads and writes binary data with a few basic helper layers.
FoundationDB has no native support for rich data types (for example `datetime` objects)
nor provides any extended data validation. FoundationDB is designed to have layers of
abstraction built on top of it to provide additional features.

The premise of `gateaux` is that where you currently have, in `fdb` library terms,
`tr[(some, data)] = (other, arbitrary, data)` of unstructured data is to enforce strict
standardisation of data in these tuples while allowing more complex types (datetime,
ipaddress etc.). In addition, the concept of structures allows for easier developer
comprehension of what data is being stored in what FoundationDB keyspace. `gateaux` has
a lot of code for not much of an interface, but it is designed to enforce structure and
types and therefore is over-engineered and over-tested by design so you don't have to
worry about your data structures in your upstream applications which use `gateaux`.

If you use `gateaux` your Python FoundationDB client code should look mostly the same,
you just can't mistakenly pack the wrong type or make mistakes before writing data. Such
additional validation is useful for larger codebases where you may be storing hundreds
of `key=value` formats into FoundationDB and keeping track of them can be challenging.

`gateaux` is a pure Python 3 (>=3.6) library which provides rich data type handling and
validation on top of the usual `pack()` and `unpack()` methods and extends the
`fdb.tuple` built-in layer. It is loosely modelled from the interfaces to relational
database object-relational mapper (RDBMS ORM) systems. Each `gateaux` structure
(comparable to a "model" in the ORM world) effectively formats one single key/value pair
at a time with more rigid validation than the `fdb` library provides out of the box.

`gateaux` does not handle FoundationDB connections for you, just the data parsing
part of your application. Effectively `gateaux` is just a data schema enforcing fancy
wrapper that sits on top of tuple packing and unpacking with some nice syntactic sugar.
`gateaux` does not abstract away any of the useful existing `fdb` keyspace interface.

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


## Examples

* [General example usage](/examples/general.py)
* [FoundationDB class scheduling example rebuilt with gateaux](/examples/class_scheduling.py)
* [FoundationDB temperature readings example rebuilt with gateaux](/examples/temperature_readings.py)


## Enforced data format

`gateaux` enforces certain requirements. These are not suitable for every project so
check carefully and verify the library is appropriate for your application before you
use it:

1. All structures are in their own FoundationDB subspace, but it is up to you what
   keyspace or subspace to use
2. Key tuple members are variable, a key of 3 elements can contain 1, 2 or 3 values,
   this is to support prefixes and ranges for keys
3. Value tuple members are fixed, a value of 3 elements must always contain 3 values
3. Validation is strict, if you define a field as a StringField you cannot store bytes
   in it etc.
4. While possible to support multiple data types, such as cast int(1) to str('1') if an
   integer is provided to a StringField, by design typing is enforced and this will
   raise an exception
5. You should not use direct binary data with FoundationDB while using `gateaux`, always
   use tuples of other types, `tr[b'key'] = b'value` is incompatible with `gateaux`, but
   `tr[(b'key',)] = (b'value',)` is compatible.

`gateaux` conforms to the same idea of `fdb.tuple` such that packing then unpacking a
tuple should always result in the same original tuple of data.


## Structures

There is only one base structure which is inherited to create your own structures.
Synopsis:

```python
import fdb
import gateaux

fdb.api_version(620)
db = fdb.open()

class SomeUserStructure(gateaux.Structure):
    key = (gateaux.BinaryField(),)
    value = (gateaux.BinaryField(),)

some_keyspace = fdb.Subspace(('some', 'subspace'))
some_structure_instance = SomeUserStructure(some_keyspace)
```

Structures have one required argument, a FoundationDB subspace. Structure instances
have the following interface for tuples:

* `structure.pack_key((...))` validates a tuple of data against the defined key
  fields and returns bytes. The bytes are a FoundationDB packed tuple in the defined
  directory.
* `structure.unpack_key(b'...')` unpacks FoundationDB bytes into a tuple and then
  validates the data against the defined key fields returning the appropriate data type
  for the field.
* `structure.pack_value((...))` validates a tuple of data against the defined value
  fields and returns bytes. The bytes are a FoundationDB packed tuple in the defined
  directory.
* `structure.unpack_value(b'...')` unpacks FoundationDB bytes into a tuple and then
  validates the data against the defined value fields returning the appropriate data
  type for the field.

And the following interface for dicts:

* `structure.pack_key_dict({...})` validates a dict of data against the defined key
  fields and returns bytes. The bytes are a FoundationDB packed tuple in the defined
  directory. To use key dicts you must have given all of your key fields a name.
* `structure.unpack_key_dict(b'...')` unpacks FoundationDB bytes into a dict and then
  validates the data against the defined key fields returning the appropriate data type
  for the field. To use key dicts you must have given all of your key fields a name.
* `structure.pack_value_dict((...))` validates a dict of data against the defined value
  fields and returns bytes. The bytes are a FoundationDB packed tuple in the defined
  directory. To use value dicts you must have given all of your value fields a name.
* `structure.unpack_value_dict(b'...')` unpacks FoundationDB bytes into a dict and then
  validates the data against the defined value fields returning the appropriate data
  type for the field. To use value dicts you must have given all of your value fields a
  name.

And the following properties:

* `structure.description` a property which returns a `dict` describing the model,
  including the name of the structure and any doc string as well as lists of
  descriptions for each field in the key and value. You can use this to programmatically
  inspect a structure in the future and is useful if you have many structures.


## Fields

All fields support the following arguments:

* `name=string` If set it defines a name stored for the field.

* `help_text=string` If set, help defines some optional help text to describe the data
   stored in the value.

* `null=boolean` If set to True then the field can have a `None` value. Defaults to
   False.

* `default=value` If set, defines a default for a field. The type must match the
  required type for the field. A default is only used if `null=True` and `None` is
  provided to the field.

Other field types may support more arguments.


### BinaryField

Stores bytes. Optional arguments:

* `max_length=int` If set defines the maximum number of bytes the field will store.

Accepted type: `bytes`


### IntegerField

Stores integers. Optional arguments:

* `min_value=int` If set defines the minimum number the field will accept
* `max_value=int` If set defines the maximum number the field will accept

Accepted type: `int`


### FloatField

Stores floats. Optional arguments:

* `min_value=float` If set defines the minimum number the field will accept
* `max_value=float` If set defines the maximum number the field will accept

Accepted type: `float`


### BooleanField

Stores booleans.

Accepted type: `bool`


### StringField

Stores strings. Optional arguments:

* `max_length=int` If set defines the maximum length of the field will accept

Accepted type: `str`


### DateTimeField

Stores datetime instances. Internally stored as a UNIX timestamp as floats in UTC.

Accepted type: `datetime.datetime`

Input `datetime.datetime` will be normalised to UTC and returned in UTC when read. You
should account for this in your application. Storing a `datetime.datetime` in any other
timezone will convert it to UTC when read. If the provided `datetime.datetime` instance
has no timezone info it will be assumed to be UTC.


### IPv4AddressField

Stores IPv4 addresses. Internally stored as 4 bytes.

Accepted type: `ipaddress.IPv4Address`


### IPv4NetworkField

Stores IPv4 networks. Internally stored as 5 bytes (address + prefix length).

Accepted type: `ipaddress.IPv4Network`


### IPv6AddressField

Stores IPv6 addresses. Internally stored as 16 bytes.

Accepted type: `ipaddress.IPv6Address`


### IPv6NetworkField

Stores IPv4 networks. Internally stored as 17 bytes (address + prefix length).

Accepted type: `ipaddress.IPv6Network`


### EnumField

Stores Enums. Internally stored as an integer that maps to a specified value. Required
arguments:

* `members=tuple` A mandatory tuple of ints to use as Enum members.

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

Accepted type: `int`


### UUIDField

Stores UUID instances. Internally stored as 16 bytes.

Accepted type: `uuid.UUID`


## Tests

There is a pretty comprehensive test suite. As `gateaux` is designed to pack and unpack
important data it has good coverage to make sure it's behaving as expected. You can run
it by cloning this repository then executing:

```bash
$ ./run-tests.sh
```

The tests perform type checking and require "mypy" from http://mypy-lang.org/ to be
globally installed. E.g. `apt install mypy`.


## Contributing

All properly formatted and sensible pull requests, issues and comments are welcome.
