.. gramfuzz documentation master file, created by
   sphinx-quickstart on Sun Dec 11 23:19:53 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gramfuzz - A grammar-based fuzzing library
====================================

gramfuzz allows one to define grammars and use them to
generate random data for fuzzing.

.. _tldr_example:

TLDR Example
^^^^^^^

Suppose we define a grammar for generating names and their prefixes
and suffixes:

.. code-block:: python

    # names_grammar.py
    from gramfuzz.fields import *

    class NRef(Ref):
        cat = "name_def"
    class NDef(Def):
        cat = "name_def"

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
    NDef("name_prefix", Or("Sir", "Ms", "Mr"))
    NDef("first_name", Or("Henry", "Susy"))
    NDef("middle_initial", String(min=1, max=2), ".")
    NDef("last_name", Or("Blart", "Tralb"))
    NDef("name_suffix", Or("Phd.", "II", "III"))

We could then use this grammar like so:

.. code-block:: python

   import gramfuzz

   fuzzer = gramfuzz.GramFuzzer()
   fuzzer.load_grammar("names_grammar.py")
   names = fuzzer.gen(cat="name", num=10)
   print("\n".join(names))

Which would output something like this:

.. code-block:: text

    Susy
    Henry Blart
    Susy J. Tralb Phd.
    Ms Susy p. Tralb Phd.
    Henry Blart II
    Henry T. Blart
    Sir Susy D.
    Ms Henry Blart II
    Susy Z. Phd.
    Susy Tralb

Table of Contents
^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   gramfuzz
   fields
   utils
   rand
   python_example
   png_example



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
