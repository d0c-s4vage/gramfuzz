#!/usr/bin/env python
# encoding: utf-8


"""
Gramfuzz utility functions
"""


import six
import sys


import gramfuzz


def val(val, pre=None, shortest=False):
    """Build the provided value, while properly handling
    native Python types, :any:`gramfuzz.fields.Field` instances, and :any:`gramfuzz.fields.Field`
    subclasses.

    :param list pre: The prerequisites list
    :returns: str
    """
    if pre is None:
        pre = []

    fields = gramfuzz.fields
    MF = fields.MetaField
    F = fields.Field
    if type(val) is MF:
        val = val()

    if isinstance(val, F):
        val = val.build(pre, shortest=shortest)

    # for ints, floats, etc
    if not isinstance(val, six.string_types) \
            and not isinstance(val, six.binary_type):
        val = str(val)

    return binstr(val)


def binstr(val):
    """Ensure that ``val`` is of type ``bytes``
    """
    if isinstance(val, six.binary_type):
        return val
    if sys.version_info < (3, 0):
        return bytes(val)
    else:
        return bytes(val, 'utf8')


def maybe_binstr(val):
    """Maybe convert ``val`` to a binary string **IF** the value is a string
    type
    """
    if not isinstance(val, six.string_types):
        return val
    return binstr(val)
