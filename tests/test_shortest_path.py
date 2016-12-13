#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Test the shortest path functionality
"""


import os
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
            "blah"
        ))
        test2 = Def("test2", "blah2")

        self.fuzzer.find_shortest_paths("default")

        for x in xrange(100):
            res = test1.build(shortest=True)
            self.assertEqual(res, "blah")


if __name__ == "__main__":
    unittest.main()
