

rand
====

Gramfuzz uses a simple module (``rand``) as an interface
to Python's built-in ``random`` module.

Since all random actions/function calls get piped through
:any:`gramfuzz.rand`, enforcing a random seed to be used
across all of gramfuzz is a simple matter.


rand Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: gramfuzz.rand
   :members:
