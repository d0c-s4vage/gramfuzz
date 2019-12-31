#!/usr/bin/env python
# encoding: utf-8

"""
This script will generate N instances of the specified grammar.
"""

import argparse
import glob
import os
import sys
import six

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gramfuzz


def generate(grammar=None, num=1, output=sys.stdout, max_recursion=10, seed=None):
    """Load and generate ``num`` number of top-level rules from the specified grammar.

    :param list grammar: The grammar file to load and generate data from
    :param int num: The number of times to generate data
    :param output: The output destination (an open, writable stream-type object. default=``sys.stdout``)
    :param int max_recursion: The maximum reference-recursion when generating data (default=``10``)
    :param int seed: The seed to initialize the PRNG with. If None, will not initialize it.
    """
    if seed is not None:
        gramfuzz.rand.seed(seed)

    fuzzer = gramfuzz.GramFuzzer()
    fuzzer.load_grammar(grammar)

    cat_group = os.path.basename(grammar).replace(".py", "")

    results = fuzzer.gen(cat_group=cat_group, num=num, max_recursion=max_recursion)
    for res in results:
        output.write(res)


def main(argv):
    parser = argparse.ArgumentParser(
        __file__,
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )
    grammar_choices = [
        os.path.basename(x).replace(".py", "") \
            for x in glob.glob(os.path.join(os.path.dirname(__file__), "grams", "*.py"))
    ]
    parser.add_argument("-g", "--grammar",
        help     = "The grammar to load. One of: {}".format(
            ",".join(grammar_choices)
        ),
        metavar  = "GRAMMAR",
        choices  = grammar_choices,
        default  = None,
        required = True,
    )
    parser.add_argument("-n", "--number",
        metavar = "N",
        help    = "The number of times to generate top-level nodes from the specified grammar(s) (default=1)",
        type    = int,
        default = 1,
    )
    parser.add_argument("-s", "--seed",
        metavar = "RAND_SEED",
        help    = "The random seed to initialize the PRNG with (default=None)",
        type    = int,
        default = None,
    )
    parser.add_argument("--max-recursion",
        metavar = "R",
        help    = "The maximum reference recursion depth allowed (default=10)",
        type    = int,
        default = 10,
    )
    if six.PY3:
        default_output = sys.stdout.buffer
    else:
        default_output = sys.stdout
    parser.add_argument("-o", "--output",
        metavar  = "OUTPUT",
        help     = "The output file to output the generated data to (default=stdout)",
        default  = default_output,
        required = False,
        type     = argparse.FileType("wb"),
    )
    args = parser.parse_args(argv)

    generate(
        grammar       = os.path.join(os.path.dirname(__file__), "grams", args.grammar + ".py"),
        num           = args.number,
        output        = args.output,
        max_recursion = args.max_recursion,
        seed          = args.seed,
    )

    
if __name__ == "__main__":
    main(sys.argv[1:])
