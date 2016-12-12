
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

gramfuzz Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: gramfuzz
   :members:
