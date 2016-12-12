
fields
============

Much of the core of gramfuzz lies in the field definitions.

Unlike other data-parsing libraries (such as `pfp <https://github.com/d0c-s4vage/pfp>`_),
gramfuzz only defines the most basic data types to be used for
grammar-driven data generation.

Classes
^^^^^^^

Int/UInt/Float/UFloat
--------

The :any:`gramfuzz.fields.Int`, :any:`gramfuzz.fields.UInt`, :any:`gramfuzz.fields.Float`,
and :any:`gramfuzz.fields.UFloat` classes are the only numeric classes defined in gramfuzz.

Most things can be accomplished using these classes, their ``min``/``max`` settings,
and their ``odds`` settings.

String
-------

The :any:`gramfuzz.fields.String` class can be used to generate arbitrary-length strings. All of the
settings from the ``Int`` class still apply to the ``String`` class (``min``, ``max``,
``odds``), except that they influence the length of the string, not the characters
it contains.

The ``String`` class has another paramter: ``charset``. This is used to specify
which characters should make up the random strings. Several pre-defined charsets
exist within the ``String`` class:

* ``charset_alpha_lower``
* ``charset_alpha_upper``
* ``charset_alpha``
* ``charset_spaces``
* ``charset_num``
* ``charset_alphanum``
* ``charset_all``

For example:

.. code-block:: python

   s = String(charset="abcdefg", min=2, max=5)
   print(s.build())
   # 'aca'

And
----

The :any:`gramfuzz.fields.And` class can be used to concatenate different values
together:

.. code-block:: python

    a = And(Int, "hello")
    print(a.build())
    # '98hello'

``And`` does not take any special parameters.

Or
---

The :any:`gramfuzz.fields.Or` class can be used to choose randomly between several
different options:

.. code-block:: python

   o = Or(Int, "Hello")
   for x in xrange(10):
       print(o.build())
   # Hello
   # Hello
   # -91
   # -60
   # 68
   # Hello
   # 13
   # Hello
   # Hello
   # Hello

Join
----

The :any:`gramfuzz.fields.Join` class can be used to join values together using a
separator. It also has a ``max`` value that can be used to indicate how many
times the first value should be repeated (any values other than the first one
will be ignored):

.. code-block:: python
    
   j = And(
       "some_function(",
       Join(
           Or(Int|Q(String)),
       sep=", ", max=5),
       ")"
   )
   
   for x in xrange(10):
       print(j.build())
   # some_function(-4294967294, "sEaKWSOGabHf", "ZkLXWYAUyEuW", 95, "FHnVYTvB")
   # some_function("koBklVcoJbDC", -60)
   # some_function(-65537)
   # some_function(96)
   # some_function(-87, -82, "x", "LKvYXEJHegjMGh")
   # some_function("TSMQeGZbXNH")
   # some_function(-254, -55, -91, "N")
   # some_function(-44, 84, 59, "FBPHBf", "NBZxlVq")
   # some_function("BvASDsxrTnycyLBChsM", "p")
   # some_function(-85, "X", "HiGdE", "XgJoNBk", 254)

Q
---

The :any:`gramfuzz.fields.Q` class can be used to surround values in quotes, optionally
specifying one of two string-escaping methods:

.. code-block:: python

    print(Q(String).build())
    # "znFHLTkwgniAXtNhI"
    print(Q("'he\"llo'", escape=True).build())
    # '\'he"llo\''"
    print(Q("<h1>'hello'</h1>", html_js_escape=True).build())
    # '\x3ch1\x3e\'hello\'\x3c/h1\x3e'

* ``escape`` - use Python's repr to escape the string
* ``html_js_escape`` - use Python's ``"string_escape"`` encoding, as well as replacing ``<``
    and ``>`` with their escaped hex formats

The ``Q`` class also accessts a ``quote`` keyword argument. This only applies if none
of the escaping methods are specified, and is merely prepended and appended to the
string.

Opt
---

The :any:`gramfuzz.fields.Opt` inherits from the ``And`` class can be used to
wrap values, optionally raising an ``OptGram`` exception when built.

If an ``OptGram`` exception is raised, the current value being built will be ignored.

.. code-block:: python

   j = And(
       "some_function(",
       Join(
           Int,
           Q(String),
           Opt(Float), # optional argument
       sep=", ", max=5),
       ")"
   )

Details
^^^^^^^

Field Base Class
----------------

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
--------------------

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
......

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
----

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

gramfuzz.fields Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: gramfuzz.fields
    :members:
