#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import gramfuzz
from gramfuzz.fields import *


class TestFuzzer(unittest.TestCase):
    def setUp(self):
        gramfuzz.GramFuzzer.__instance__ = None
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

        self.fuzzer.preprocess_rules()

        self.assertNotIn("a", self.fuzzer.defs["default"])
        self.assertIn("c", self.fuzzer.defs["default"])

    def test_prune_rules_circular(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(r"""
import gramfuzz
from gramfuzz.fields import *

# should get pruned since b isn't defined
Def("a", Ref("b"))
Def("b", Ref("c"))
Def("c", Ref("a"))
        """)
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        self.fuzzer.preprocess_rules()

        self.assertNotIn("a", self.fuzzer.defs["default"])
        self.assertNotIn("b", self.fuzzer.defs["default"])
        self.assertNotIn("c", self.fuzzer.defs["default"])
    
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

    # see #4 - auto process during gen()
    def test_auto_process(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(r"""
import gramfuzz
from gramfuzz.fields import *

Def("test", "hello")
# should also get pruned
Def("other_test", Ref("not_reachable", cat="other"))
# should get pruned
Def("not_reachable", Ref("doesnt_exist", cat="other"), cat="other")
        """)
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        self.assertTrue(self.fuzzer._rules_processed == False)

        data = self.fuzzer.gen(cat="default", num=1)[0]

        self.assertTrue(self.fuzzer._rules_processed == True)

        with self.assertRaises(gramfuzz.errors.GramFuzzError) as ctx:
            self.fuzzer.get_ref("other", "not_reachable")
        self.assertEqual(
            ctx.exception.message,
            "referenced definition ('not_reachable') not defined"
        )


if __name__ == "__main__":
    unittest.main()
