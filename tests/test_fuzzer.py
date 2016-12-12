#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import gramfuzz
from gramfuzz.fields import *


class TestFields(unittest.TestCase):
    def setUp(self):
        self.fuzzer = gramfuzz.GramFuzzer()
    
    def tearDown(self):
        pass

    def test_prune_rules(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(r"""
import gramfuzz
from gramfuzz.fields import *

# should get pruned since b isn't defined
Def("a", UInt, Ref("b"))
Def("c", UInt)
        """)
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        self.fuzzer.prune(["default"], "default")

        self.assertNotIn("a", self.fuzzer.defs["default"])
        self.assertIn("c", self.fuzzer.defs["default"])
    
    def test_load_grammar(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(r"""
import gramfuzz
from gramfuzz.fields import *

Def("test_def", Join(Int, Int, Opt("hello"), sep="|"))
Def("test_def", Join(Float, Float, Opt("hello"), sep="|"))
Def("test_def_ref", "this.", String(min=1), "=", Q(Ref("test_def")))
        """)
        named_tmp.flush()

        self.fuzzer.load_grammar(named_tmp.name)

        named_tmp.close()

        res = self.fuzzer.get_ref("default", "test_def_ref").build()


if __name__ == "__main__":
    unittest.main()
