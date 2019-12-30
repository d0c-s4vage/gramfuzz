#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Ensure the example grammars and scripts still work correctly!
"""


import glob
import os
import random
import subprocess
import sys
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import gramfuzz
from gramfuzz.fields import *
import gramfuzz.utils as gutils


class TestExamples(unittest.TestCase):
    def tearDown(self):
        pass

    def test_examples(self):
        example_script = os.path.join(os.path.dirname(__file__), "..", "examples", "example.py")

        # basically just don't error out on anything
        for gram_path in glob.glob(os.path.join(os.path.dirname(__file__), "..", "examples", "grams", "*.py")):
            seed = random.randint(0, 0xffffffff)
            gram_name = os.path.basename(gram_path).replace(".py", "")

            proc = subprocess.Popen(["python", example_script,
                "--grammar", gram_name,
                "--num", str(10),
                "--max-recursion", str(10),
                "--seed", str(seed)
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout,_ = proc.communicate()

            self.assertNotIn(b"ERROR", stdout)


if __name__ == "__main__":
    unittest.main()
