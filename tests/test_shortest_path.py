#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Test the shortest path functionality
"""


import os
import six
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gramfuzz
from gramfuzz.fields import *


class TestShortestPath(unittest.TestCase):
    def setUp(self):
        self.fuzzer = gramfuzz.GramFuzzer()

    def tearDown(self):
        pass

    def test_basic(self):
        test1 = Def("test1", Or(
            Ref("test2"),
            And(Ref("test2"), Ref("test1")),
            b"blah" # <-- this blah should be generated
        ))
        test2 = Def("test2", "blah2", Ref("test3"))
        test3 = Def("test3", "blah3")

        self.fuzzer._find_shortest_paths()

        for x in six.moves.range(100):
            res = test1.build(shortest=True)
            self.assertEqual(res, b"blah")

    def test_complicated(self):
        test1 = Def("test1", Or(
            Ref("test2"),
            And(Ref("test2"), Ref("test1")),
            Ref("test3"),
        ))
        test2 = Def("test2", "blah2") # <-- this blah2 should be generated
        test3 = Def("test3", Ref("test2"))

        self.fuzzer._find_shortest_paths()

        for x in six.moves.range(100):
            res = test1.build(shortest=True)
            self.assertEqual(res, b"blah2")

    def test_complicated2(self):
        test1 = Def("test1", Or(
            Ref("test2"),
            And(Ref("test2"), Ref("test1")),
            Ref("test3"),
        ))
        test2 = Def("test2", Ref("test4") | Ref("test3"))
        test3 = Def("test3", Or(Ref("test2"), "blah3")) # <-- this blah3 should be generated
        test4 = Def("test4", Ref("test3"))

        self.fuzzer._find_shortest_paths()

        for x in six.moves.range(100):
            res = test1.build(shortest=True)
            self.assertEqual(res, b"blah3")

    def test_cross_category(self):
        test1 = Def("test1", Or(
            Ref("test2"),
            And(Ref("test2"), Ref("test1")),
            Ref("test3", cat="other"),
        ))
        test2 = Def("test2", Ref("test4") | Ref("test3", cat="other"))
        test3 = Def("test3", Or(Ref("test2"), "blah3"), cat="other") # <-- this blah3 should be generated
        test4 = Def("test4", Ref("test3", cat="other"))

        self.fuzzer._find_shortest_paths()

        for x in six.moves.range(100):
            res = test1.build(shortest=True)
            self.assertEqual(res, b"blah3")

    def test_grammar_optional_list(self):
        # taken from python 2.7 grammar
        fpdef = Def("fpdef",
            Or(
                Ref("name"),
                And("(", Ref("fplist"), ")")
            ),
        )
        fplist = Def("fplist",
            Ref("fpdef"), STAR(",", Ref("fpdef")), Opt(","),
        )
        Def("name", "THE NAME")

        self.fuzzer._find_shortest_paths()

        for x in six.moves.range(100):
            res = fpdef.build(shortest=True)
            self.assertEqual(res, b"THE NAME")

        for x in six.moves.range(100):
            res = fplist.build(shortest=True)
            # it may have the comma at the end
            self.assertIn(res, [b"THE NAME", b"THE NAME,"])


if __name__ == "__main__":
    unittest.main()
