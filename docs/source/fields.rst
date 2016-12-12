
fields
============

Much of the core of gramfuzz lies in the field definitions.

Unlike other data-parsing libraries (such as `pfp <https://github.com/d0c-s4vage/pfp>`_),
gramfuzz only defines the most basic data types to be used for
grammar-driven data generation.

Field Base Class
^^^^^^^^^^^^^^^^

All fields inherit from the :any:`gramfuzz.fields.Field` class.

``Field`` classes may be used in grammar rule definitions, as well as instances
of ``Field`` classes (thanks to the :any:`gramfuzz.fields.MetaField` class and the
:any:`gramfuzz.utils.val` function).

For example, defining a rule that uses the ``Int`` field with the default settings
may look something like this:

.. code-block:: python
    
    Def("integer_rule", Int)

However, if more specific settings for the ``Int`` class were desired, it may
look something like this instead:

.. code-block:: python

    Def("integer_rule", Int(min=10, max=20))

Note that this can also be abstracted to something like this:

.. code-block:: python

   SPECIAL_INT = Int(min=10, max=20)

   Def("integer_rule", SPECIAL_INT)
   Def("integer_rule2", SPECIAL_INT, ",", SPECIAL_INT)

This pattern is highly recommended and prevents one from constantly
hard-coding specific settings throughout a grammar.

Operator Overloading
^^^^^^^^^^^^^^^^^^^^

gramfuzz defines two main classes for concatenating or randomly
choosing between values: :any:`gramfuzz.fields.And` and :any:`gramfuzz.fields.Or`.

The ``And`` and ``Or`` classes can be explicitly used:

.. code-block:: python

   And(Int, ", ", Int)
   Or(Int, Float)

Or they can be used using the overloaded and and or operators:

.. code-block:: python

   (Int & ", " & Int)
   (Int | Float)

There are a few drawbacks however, mostly having to do with the fact
that gramfuzz cannot tell where the parenthesis are in more complex
scenarios, like the one below:

.. code-block:: python
    
    (Int & (Int & (Int & Int)))

Ideally, the statement above would generate something like the statement
below, which uses explicit ``And`` s:

.. code-block:: python

    And(Int, And(Int, And(Int, Int)))

When in reality, gramfuzz ends up doing this instead:

.. code-block:: python

   And(Int, Int, Int, Int)
   # from the python console:
   # >>> a = (Int & (Int & (Int & Int)))
   # >>> a
   # <And[<Int>,<Int>,<Int>,<Int>]>

For this reason, I tend to use the overloaded operators only in simple situations.
Complex logic/scenarious I tend to only use explicit ``And`` and ``Or``.

Gotcha
------

One important gotcha is shown below:

.. code-block:: python

   5 | Int | Float

The above example does not work because ``5`` is the first operand
in the or sequence. This is due to the way Python handles
operator overloading.

However, this *will* work:

.. code-block:: python

   Int | Float | 5

Native types can only be used with the ``Field`` overloaded operators
if they are not the first operand.

Odds
^^^^

The :any:`gramfuzz.fields.Int`, :any:`gramfuzz.fields.UInt`, :any:`gramfuzz.fields.Float`,
:any:`gramfuzz.fields.UFloat`, and :any:`gramfuzz.fields.String` classes each make use of
the :any:`gramfuzz.fields.Field.odds` member when generating data, as well as (optionally)
``min`` and ``max`` members.

An example of using the ``odds`` member can be seen in the default values
for the ``Int``, ``Float``, and ``String`` classes:

.. code-block:: python

    class Float(Int):
        # ...
        odds = [
            (0.75,    [0.0,100.0]),        # 75% chance of being in the range [0.0, 100.0)
            (0.05,    0),                  # 5% chance of having the value 0
            (0.10,    [100.0, 1000.0]),    # 10% chance of being in the range [100.0, 1000.0)
            (0.10,    [1000.0, 100000.0]), # 10% chance of being in the range [1000.0, 100000.0)
        ]
        # ...

It should be noted that the probability percents in each entry in
the ``odds`` list should add up to ``1.0``.

See the documentation below for more details:

* :any:`gramfuzz.fields.Field.odds`
* :any:`gramfuzz.fields.Int.__init__` (for min/max)

Int/UInt/Float/UFloat
^^^^^^^^

The :any:`gramfuzz.fields.Int`, :any:`gramfuzz.fields.UInt`, :any:`gramfuzz.fields.Float`,
and :any:`gramfuzz.fields.UFloat` classes are the only numeric classes defined in gramfuzz.

Most things can be accomplished using these classes, their ``min``/``max`` settings,
and their ``odds`` settings.

gramfuzz.fields Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: gramfuzz.fields
    :members:
