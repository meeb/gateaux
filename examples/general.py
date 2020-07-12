#!/usr/bin/env python3
'''
    This example details the general interface for structures and how they can be used.
    As a summary, you would just replace fdb.tuple.[un]pack with the .pack_[key|value]
    method of your defined structure.
'''


from datetime import datetime, timedelta
from ipaddress import IPv4Address
import fdb
import gateaux


# Connect to your FoundationDB cluster
fdb.api_version(510)
db = fdb.open()
# Create or open a directory, subspace, or any other FoundationDB keyspace
event_log_space = fdb.directory.create_or_open(('log', 'events'))


# Define a data structure, an example event log in this case
class EventLog(gateaux.Structure):

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
        gateaux.IPv4AddressField(
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


# Create an EventLog instance using the defined keyspace as the only argument, this can
# be the root FoundationDB connection (in which case EventLog will not have any prefix
# for its keys) or a directory or a subspace
event_log = EventLog(event_log_space)


# Use the structure
@fdb.transactional
def store_event(tr, ipv4, num_bytes, event_type):
    key = event_log.pack_key((datetime.now(), ipv4))
    value = event_log.pack_value((num_bytes, event_type))
    tr[key] = value

store_event(db, IPv4Address('127.0.0.1'), 12345, EventLog.TYPE_UPLOAD))


# All available methods at once
@fdb.transactional
def complete_example(tr):
    key_tuple = (datetime.now(), IPv4Address('127.0.0.1'))
    value_tuple = (12345, EventLog.TYPE_UPLOAD)
    # Packing
    packed_key = event_log.pack_key(key_tuple)
    packed_value = event_log.pack_value(value_tuple)
    # Unpacking
    unpacked_key = event_log.unpack_key(packed_key)
    unpacked_value = event_log.unpack_value(packed_value)
    # After packing and unpacking they are the same
    assert(key_tuple == unpacked_key)
    assert(value_tuple == unpacked_value)

complete_example(db)


# Exception handling
@fdb.transactional
def complete_example(tr):
    try:
        # Attempting to put a string into a DateTime field
        key_tuple = ('wrong type, not a datetime', IPv4Address('127.0.0.1'))
        packed_key = event_log.pack_key(key_tuple)
    except gateaux.errors.ValidationError as e:
        # ... handle the error
        print('validation error', e)
