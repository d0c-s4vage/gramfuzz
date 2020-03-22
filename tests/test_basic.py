#!/usr/bin/env python
# encoding: utf-8


import functools
import os
import re
import six
import sys
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import gramfuzz
from gramfuzz.fields import *
import gramfuzz.utils as gutils


LOOP_NUM = 1000
PERCENT_ERROR = 0.1


def loop(fn):
    @functools.wraps(fn)
    def looper(*args, **kwargs):
        for x in six.moves.range(LOOP_NUM):
            fn(*args, **kwargs)

    return looper


class TestFields(unittest.TestCase):
    def setUp(self):
        gramfuzz.GramFuzzer.__instance__ = None
    
    def tearDown(self):
        pass
    
    @loop
    def test_int(self):
        i = Int
        res = i().build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^(-)?\d+$'))
    
    @loop
    def test_uint(self):
        i = UInt
        res = i().build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^\d+$'))

    @loop
    def test_int_min_max(self):
        min_ = 0
        max_ = 65535

        i = Int(min=min_, max=max_)
        res = i.build()

        self.assertTrue(min_ <= res < max_, "{} <= {} < {} was not True".format(
            min_,
            res,
            max_
        ))

    @loop
    def test_uint_min_max(self):
        min_ = 100
        max_ = 110

        i = UInt(min=min_, max=max_)
        res = i.build()

        self.assertTrue(min_ <= res < max_, "{} <= {} < {} was not True".format(
            min_,
            res,
            max_
        ))

    @loop
    def test_uint_min_max2(self):
        default_min = 0
        max_ = 110

        i = UInt(max=max_)
        res = i.build()

        self.assertTrue(default_min <= res < max_, "{} <= {} < {} was not True".format(
            default_min,
            res,
            max_
        ))

    def test_int_odds(self):
        odds_results = {}

        i = UInt(odds=[
            (0.25, (0, 10)),
            (0.25, (10, 20)),
            (0.25, (20, 30)),
            (0.25, (30, 40))
        ])
        for x in six.moves.range(LOOP_NUM):
            res = i.build()
            odds_group = res // 10
            # should only be four groups
            self.assertIn(odds_group, [0,1,2,3])
            odds_results.setdefault(odds_group, 0)
            odds_results[odds_group] += 1

        for x in six.moves.range(4):
            group_percent = odds_results[x] / float(LOOP_NUM)
            percent_off = abs(group_percent - 0.25)
            self.assertLess(percent_off, PERCENT_ERROR, "{}/{} == {}% error, bad".format(
                odds_results[x],
                LOOP_NUM,
                percent_off
            ))

    def test_int_odds_types(self):
        """Test different probability types (range vs single value)
        """
        odds_results = {}

        i = UInt(odds=[
            (0.50, (0, 10)),
            (0.50, 15),
        ])
        LOOP_NUM = 10000
        for x in six.moves.range(LOOP_NUM):
            res = i.build()
            odds_group = res // 10
            # should only be four groups
            self.assertIn(odds_group, [0,1])
            odds_results.setdefault(odds_group, 0)
            odds_results[odds_group] += 1

        for x in six.moves.range(2):
            group_percent = odds_results[x] / float(LOOP_NUM)
            percent_off = abs(group_percent - 0.50)
            self.assertLess(percent_off, PERCENT_ERROR, "{}/{} == {}% error, bad".format(
                odds_results[x],
                LOOP_NUM,
                percent_off
            ))
    
    @loop
    def test_float(self):
        f = Float
        res = f().build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^(-)?\d+(\.\d+)?$'))
    
    @loop
    def test_ufloat(self):
        f = UFloat
        res = f().build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^\d+(\.\d+)?$'))
    
    @loop
    def test_string_charset(self):
        s = String(charset="abc")
        res = s.build()
        self.assertRegexpMatches(res, gutils.binstr(r'^[abc]*$'))
    
    @loop
    def test_string_min_max(self):
        s = String(min=3, max=5)
        res = s.build()
        self.assertIn(len(res), [3,4])
    
    def test_string_odds(self):
        odds_results = {}

        s = String(odds=[
            (0.25, (0, 10)),
            (0.25, (10, 20)),
            (0.25, (20, 30)),
            (0.25, (30, 40))
        ])
        for x in six.moves.range(LOOP_NUM):
            res = s.build()
            odds_group = len(res) // 10
            # should only be four groups
            self.assertIn(odds_group, [0,1,2,3])
            odds_results.setdefault(odds_group, 0)
            odds_results[odds_group] += 1

        for x in six.moves.range(4):
            group_percent = odds_results[x] / float(LOOP_NUM)
            percent_off = abs(group_percent - 0.25)
            self.assertLess(percent_off, PERCENT_ERROR, "{}/{} == {}% error, bad".format(
                odds_results[x],
                LOOP_NUM,
                percent_off
            ))
    
    def test_join_native(self):
        j = Join("a", "b", sep=",")
        res = j.build()
        self.assertEqual(res, b"a,b")

    @loop
    def test_join_fields(self):
        j = Join(UInt, "b", sep=",")
        res = j.build()
        self.assertRegexpMatches(res, gutils.binstr(r'^\d+,b'))

    @loop
    def test_join_fields2(self):
        j = Join(UInt, "b", sep="X")
        res = j.build()
        self.assertRegexpMatches(res, gutils.binstr(r'^\d+Xb'))

    def test_join_max(self):
        num_items = {}
        for x in six.moves.range(LOOP_NUM):
            # should generate 0-9 items, not 10
            j = Join(UInt, sep=",", max=10)
            res = j.build()
            self.assertRegexpMatches(res, gutils.binstr(r'^\d+(,\d+)*'))
            sep_count = res.count(b",")
            num_items.setdefault(sep_count, 0)
            num_items[sep_count] += 1

        self.assertEqual(len(num_items), 10)

        for k,v in six.iteritems(num_items):
            percent = v / float(LOOP_NUM)
            diff = abs(percent - 0.10)
            self.assertLess(diff, PERCENT_ERROR, "{}/{} == {}% error, bad".format(
                v,
                LOOP_NUM,
                diff
            ))

    @loop
    def test_and_operator(self):
        data = UInt & "," & UInt
        res = data.build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^\d+,\d+$'))
    
    @loop
    def test_and_explicit(self):
        data = And(UInt, ",", UInt)
        res = data.build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^\d+,\d+$'))

    @loop
    def test_or_operator(self):
        data = UInt | "hello"
        res = data.build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^(\d+|hello)'))

    @loop
    def test_or_explicit(self):
        data = Or(UInt, "hello")
        res = data.build()
        val = gutils.val(res)
        self.assertRegexpMatches(val, gutils.binstr(r'^(\d+|hello)'))

    def test_or_probabilities(self):
        """Make sure that Or does its probabilities correctly
        """
        # for two items, their probability of being generated should
        # be 50%

        hello_count = 0
        int_count = 0
        data = Or(UInt, "hello")

        for x in six.moves.range(LOOP_NUM):
            res = data.build()
            val = gutils.val(res)
            if val == b"hello":
                hello_count += 1
            elif re.match(gutils.binstr(r'^\d+$'), val) is not None:
                int_count += 1
            else:
                self.assertTrue(False, "was neither an int or hello")

        for v in [hello_count, int_count]:
            percent = v / float(LOOP_NUM)
            diff = abs(percent - 0.50)
            self.assertLess(diff, PERCENT_ERROR, "{}/{} == {}% error, bad".format(
                v,
                LOOP_NUM,
                diff
            ))

    def test_weighted_or_probabilities(self):
        """Make sure that WeightedOr does its probabilities correctly
        """
        counts = {
            "int": {
                "prob": 0.1,
                "val": UInt,
                "count": 0,
                "match": lambda x: re.match(gutils.binstr(r'^\d+$'), x) is not None
            },
            "hello": {
                "prob": 0.6,
                "val": b"hello",
                "count": 0,
                "match": lambda x: x == b"hello"
            },
            "a": {
                "prob": 0.3,
                "val": b"a",
                "count": 0,
                "match": lambda x: x == b"a"
            },
        }
        values = [(v["val"], v["prob"]) for k, v in counts.items()]
        data = WeightedOr(*values)

        for x in six.moves.range(LOOP_NUM):
            res = data.build()
            val = gutils.val(res)
            matched = False
            for val_name, val_info in counts.items():
                if val_info["match"](val):
                    val_info["count"] += 1
                    matched = True
            if matched is False:
                raise Exception("Something went wrong, could not match to a value")

        for val_name, val_info in counts.items():
            percent = val_info["count"] / float(LOOP_NUM)
            diff = abs(percent - val_info["prob"])
            self.assertLess(diff, PERCENT_ERROR, "{}: {}/{} == {}% error, bad".format(
                val_name,
                val_info["count"],
                LOOP_NUM,
                diff
            ))
    
    def test_opt(self):
        hello_count = 0
        data = Join(UInt, Opt("hello"), sep="|")

        for x in six.moves.range(LOOP_NUM):
            res = data.build()
            if b"hello" in res:
                hello_count += 1

        hello_percent = hello_count / float(LOOP_NUM)
        diff = abs(hello_percent - 0.5)
        self.assertLess(diff, PERCENT_ERROR, "{}/{} == {}% error, bad".format(
            hello_count,
            LOOP_NUM,
            diff
        ))
    
    def test_q_normal(self):
        data = Q("hello")
        res = data.build()
        self.assertEqual(b'"hello"', res)
    
    def test_q_html_escape(self):
        data = Q("<script>hello\'\"", html_js_escape=True)
        res = data.build()
        self.assertEqual(b'\'\\x3cscript\\x3ehello\\\'"\'', res)
    
    def test_q_escape(self):
        data = Q("'hello'", escape=True)
        res = data.build()
        self.assertEqual(b'"\'hello\'"', res)

        data = Q('"hello"', escape=True)
        res = data.build()
        self.assertEqual(b'\'"hello"\'', res)
    
    def test_def(self):
        def1 = Def("test", Int & "-" & String, cat="test_def")

        fuzzer = gramfuzz.GramFuzzer.instance()
        fetched_def = fuzzer.get_ref(cat="test_def", refname="test")

        self.assertEqual(def1, fetched_def)


if __name__ == "__main__":
    unittest.main()
