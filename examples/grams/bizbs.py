#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Generate business BS statements. Inspired/adopted from
http://www.atrixnet.com/bs-generator.html
"""


import os
from gramfuzz.fields import *


TOP_CAT = "bizbs"


def load_words(filename):
    data_dir = os.path.join(os.path.dirname(__file__), "bizbs_data")
    with open(os.path.join(data_dir, filename), "r") as f:
        data = f.read()

    res = []
    for line in data.split("\n"):
        line = line.strip()
        if line == "":
            continue
        res.append(line)
    return res


def make_present_participles(verbs):
    """Make the list of verbs into present participles

    E.g.:

        empower -> empowering
        drive -> driving
    """
    res = []
    for verb in verbs:
        parts = verb.split()
        if parts[0].endswith("e"):
            parts[0] = parts[0][:-1] + "ing"
        else:
            parts[0] = parts[0] + "ing"
        res.append(" ".join(parts))
    return res


adverbs = load_words("adverbs.txt")
verbs = load_words("verbs.txt")
present_participles = make_present_participles(verbs)
adjectives = load_words("adjectives.txt")
nouns = load_words("nouns.txt")
sub_conjunctions = load_words("subordinating_conjunctions.txt")


class BDef(Def):
    cat = "bizbs_def"
class BRef(Ref):
    cat = "bizbs_def"


Def("bizbs_phrase",
    BRef("bizbs_part"),
    Opt(
        BRef("sub_conjunction"),
        " ",
        BRef("bizbs_part_pres_participle")
    ),
    "\n",
sep=" ", cat="bizbs")

BDef("bizbs_part",
    Opt(BRef("adverb")),
    BRef("verb"),
    Opt(BRef("adjective")),
    BRef("noun"),
sep=" ")

BDef("bizbs_part_pres_participle",
    Opt(BRef("adverb")),
    BRef("present_participle"),
    Opt(BRef("adjective")),
    BRef("noun"),
sep=" ")

BDef("adverb", Or(*adverbs))
BDef("verb", Or(*verbs))
BDef("adjective", Or(*adjectives))
BDef("noun", Or(*nouns))
BDef("sub_conjunction", Or(*sub_conjunctions))
BDef("present_participle", Or(*present_participles))
