
gramfuzz
========

Using gramfuzz consists of three steps:

#. defining the grammar(s)
#. create a :any:`gramfuzz.GramFuzzer` instance
#. loading the grammar
#. generating ``num`` random rules from the loaded grammars from a specifc category

Example Revisited
^^^^^^^^^^^^^^^^^

In the example on the main page for this documentation (:ref:`tldr_example`),
we defined a grammar, and made two new classes: ``NRef`` and ``NDef``.

We did this so that we could force any definitions created with
``NDef`` to use the ``"name_def"`` category. The same goes for
the ``NRef`` class we made - it forces gramfuzz to lookup referenced
definitions in the ``"name_def"`` category instead of the default
category.

The importance of this functionality becomes clear when we look at the
line that actually generates the names:

.. code-block:: python

   names = fuzzer.gen(cat="name", num=10)

Notice how we explicitly say that we want the fuzzer to generate ``10`` random
rules from the ``"name"`` category (*NOT* the ``"name_def"`` category). This
is an intentional way of differentiating between top-level rules that
should be chosen randomly to generate, and rules that only exist to
help create the top-level rules.

In our simple names example, the sole rule definition in the ``"name"`` category:

.. code-block:: python

    Def("name",
        Join(
            Opt(NRef("name_prefix")),
            NRef("first_name"),
            Opt(NRef("middle_initial")),
            Opt(NRef("last_name")),
            Opt(NRef("name_suffix")),
        sep=" "),
        cat="name"
    )

uses the other definitions in the ``"name_def"`` category to complete itself.

Preferred Category Groups
^^^^^^^^^^^^^^^^^^^^^^^^

gramfuzz has a concept of a "category group". In the default usage of this concept,
a grammar-rule's category group is the name of the python file the rule was defined
in.

If, say, we had loaded ten separate grammar files into a ``GramFuzzer`` instance,
and one of the grammar files was named ``important_grammar.py``, we could tell
the fuzzer to focus on all the rules in that grammar 60% of the time:

.. code-block:: python

    # assuming we've already loaded all of the grammars
    outputs = fuzzer.gen(
        cat             = "the_category",
        num             = 10,
        preferred       = ["important_grammar"],
        preferred_ratio = 0.6
    )

This becomes especially powerful when using the gramfuzz module as
a base for more specific/targeted grammar fuzzing.

Rule Preprocessing
^^^^^^^^^^^^^^^^^^

Another argument to the :any:`gramfuzz.GramFuzzer.gen` function is the
``auto_process`` parameter, which defaults to ``True``.

When true, the ``GramFuzzer`` instance will calculate the reference paths lengths
of each rule, as well as which option in each ``Or``
field is the shortest/most direct to generate.

Once this is complete, ``GramFuzzer`` will prune all rules that it could
not determine a reference length for. This would indiciate that the rule
could never terminate in a leaf node/rule, and thus should be removed.

If any new grammar rules are added to the ``GramFuzzer`` instance, it
will rerun the :any:`gramfuzz.GramFuzzer.preprocess_rules` method
the next time ``gen`` is called.

Maximum Recursion
^^^^^^^^^^^^^^^^^

The :any:`gramfuzz.GramFuzzer.gen` method has an argument ``max_recursion``.
This argument is used to limit the number of times a :any:`gramfuzz.fields.Ref`
instance may resolve nested references.

For example the code below:

.. code-block:: python

    import gramfuzz
    from gramfuzz.fields import *
    import sys

    class ODef(Def): cat = "other"
    class ORef(Ref): cat = "other"

    fuzzer = gramfuzz.GramFuzzer()

    rule1 = Def("rule1", Or("rule1", ORef("rule2")))
    ODef("rule2", Or("rule2", ORef("rule3")))
    ODef("rule3", Or("rule3", ORef("rule4")))
    ODef("rule4", Or("rule4", ORef("rule5")))
    ODef("rule5", "rule5")

    max_recursion = int(sys.argv[1])
    for x in range(10000):
        print(fuzzer.gen("default", num=1, max_recursion=max_recursion)[0])

yields the output:

.. code-block:: text

    !python test.py 5 | sort | uniq -c
       4951 rule1
       2473 rule2
       1287 rule3
        649 rule4
        640 rule5


Now if we limit ``max_recursion`` to ``2``, you'll see that it only
generates ``rule1`` and ``rule2``:

.. code-block:: text

    !python test.py 2 | sort | uniq -c
       4935 rule1
       5065 rule2

Once it reaches ``rule2``, the reference level count will have reached
a value of ``2``, at which point instead of randomly choosing to generate either
the value ``rule2`` or ``ORef("rule3")``, it will choose the field with
the shortest number of dereferences back to a leaf value. In this case,
it will choose to generate ``rule3`` since it *is* a leaf value and does
not require any dereferencing.

In a more real-world example, grammars often define lists of items
in a recursive manner, like below (taken from the Python 2.7 syntax
grammar):

.. code-block:: text

    fpdef: NAME | '(' fplist ')'
    fplist: fpdef (',' fpdef)* [',']

If this were implemented in gramfuzz, it would look like this:

.. code-block:: python
    
    Def("fpdef", Or(
        Ref("name"),
        And("(", Ref("fplist"), ")")
    ))
    Def("fplist",
        Ref("fpdef"), STAR(", ", Ref("fpdef")), Opt(", "),
    )

Without the max_recursion limits, this could easily result in a
maximum recursion depth runtime error in Python (and often does).
The ``max_recursion`` limit was specifically added to handle these
types of situations.

gramfuzz Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: gramfuzz
   :members:
