#!/usr/bin/env python
# encoding: utf-8


import os
import shutil
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import gramfuzz
from gramfuzz.fields import *
import gramfuzz.utils as gutils


class TestFuzzer(unittest.TestCase):
    def setUp(self):
        gramfuzz.GramFuzzer.__instance__ = None
        self.fuzzer = gramfuzz.GramFuzzer()
    
    def tearDown(self):
        pass

    def test_set_max_recursion(self):
        self.fuzzer.set_max_recursion(100)
        self.assertEqual(Ref.max_recursion, 100)

    def test_default_cat_for_cat_group(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

TOP_CAT = "other"

# should get pruned since b isn't defined
Def("a", UInt, Ref("b", cat="other"), cat="other")
Def("c", UInt, cat="other")
        """))
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        cat_group = os.path.basename(named_tmp.name)
        named_tmp.close()

        self.assertIn(cat_group, self.fuzzer.cat_group_defaults)
        self.assertEqual(self.fuzzer.cat_group_defaults[cat_group], "other")

    def test_gen_cat_group(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

TOP_CAT = "other"

# should get pruned since b isn't defined
Def("a", "hello", cat="other")
        """))
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        cat_group = os.path.basename(named_tmp.name)
        named_tmp.close()

        res = self.fuzzer.gen(cat_group=cat_group, num=1)[0]
        self.assertEqual(res, b"hello")

    def test_prune_rules(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

# should get pruned since b isn't defined
Def("a", UInt, Ref("b"))
Def("c", UInt)
        """))
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        self.fuzzer.preprocess_rules()

        self.assertNotIn("a", self.fuzzer.defs["default"])
        self.assertIn("c", self.fuzzer.defs["default"])

    def test_no_prune_rules(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

# should get pruned since b isn't defined
Def("a", UInt, Ref("b"), no_prune=True)
Def("c", UInt)
        """))
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        self.fuzzer.preprocess_rules()

        self.assertIn("a", self.fuzzer.defs["default"])
        self.assertIn("c", self.fuzzer.defs["default"])

    def test_prune_rules_circular(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

# should get pruned since b isn't defined
Def("a", Ref("b"))
Def("b", Ref("c"))
Def("c", Ref("a"))
        """))
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        self.fuzzer.preprocess_rules()

        self.assertNotIn("a", self.fuzzer.defs["default"])
        self.assertNotIn("b", self.fuzzer.defs["default"])
        self.assertNotIn("c", self.fuzzer.defs["default"])

    # see #16 - __file__ needs to be set for grammar files that are being
    # loaded
    def test_file_set_during_grammar_load(self):
        """Ensure that __file__ is set when loading a new grammar file
        """
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
from gramfuzz.fields import *

Def("file_test", __file__, cat="default")
        """))
        named_tmp.flush()

        # should not raise an exception
        self.fuzzer.load_grammar(named_tmp.name)
        output = self.fuzzer.gen(num=1, cat="default")
        self.assertEqual(output[0], gutils.binstr(named_tmp.name))


    def test_load_grammar(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

Def("test_def", Join(Int, Int, Opt("hello"), sep="|"))
Def("test_def", Join(Float, Float, Opt("hello"), sep="|"))
Def("test_def_ref", "this.", String(min=1), "=", Q(Ref("test_def")))
        """))
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        res = self.fuzzer.get_ref("default", "test_def_ref").build()

    def test_relative_grammar_import(self):
        tmpdir = tempfile.mkdtemp()

        try:
            file1 = os.path.join(tmpdir, "file1.py")
            file2 = os.path.join(tmpdir, "file2.py")

            with open(file1, "wb") as f:
                f.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

import file2

TOP_CAT = "file1"

Def("file1def", Ref("file2def", cat=file2.TOP_CAT), cat="file1")
                """))

            with open(file2, "wb") as f:
                f.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

TOP_CAT = "file2"

Def("file2def", "hi from file2", cat="file2")
                """))

            self.fuzzer.load_grammar(file1)

            res = self.fuzzer.gen(cat_group="file1", num=1)[0]
            self.assertEqual(res, b"hi from file2")
            
        # always clean up
        finally:
            shutil.rmtree(tmpdir)

    # see #4 - auto process during gen()
    def test_auto_process(self):
        named_tmp = tempfile.NamedTemporaryFile()
        named_tmp.write(gutils.binstr(r"""
import gramfuzz
from gramfuzz.fields import *

Def("test", "hello")
# should also get pruned
Def("other_test", Ref("not_reachable", cat="other"))
# should get pruned
Def("not_reachable", Ref("doesnt_exist", cat="other"), cat="other")
        """))
        named_tmp.flush()
        self.fuzzer.load_grammar(named_tmp.name)
        named_tmp.close()

        self.assertTrue(self.fuzzer._rules_processed == False)

        data = self.fuzzer.gen(cat="default", num=1)[0]

        self.assertTrue(self.fuzzer._rules_processed == True)

        with self.assertRaises(gramfuzz.errors.GramFuzzError) as ctx:
            self.fuzzer.get_ref("other", "not_reachable")
        self.assertEqual(
            str(ctx.exception),
            "referenced definition ('not_reachable') not defined"
        )


if __name__ == "__main__":
    unittest.main()
