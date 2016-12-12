
utils
=========

gramfuzz will work with most native Python types, as well
as any :any:`gramfuzz.fields.Field` type.

gramfuzz uses the :any:`gramfuzz.utils.val` function to convert
values into data.

For native Python types, ``str()`` is used to convert the
object into a string.

For :any:`gramfuzz.fields.Field` classes, a new instance is created,
and then ``build()`` is called on the created instance.

For :any:`gramfuzz.fields.Field` instances, ``build()`` is simply
called on the instance.


utils Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: gramfuzz.utils
   :members:
