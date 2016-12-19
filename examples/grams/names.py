#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gramfuzz.fields import *


import roman_numeral


TOP_CAT = "name"


class NRef(Ref):
    cat = "name_def"
class NDef(Def):
    cat = "name_def"


Def("name",
    Opt(NRef("name_title")),
    NRef("personal_part"),
    NRef("last_name"),
    Opt(NRef("name_suffix")),
cat="name", sep=" ")
NDef("personal_part",
    NRef("initial") | NRef("first_name"), Opt(NRef("personal_part")),
sep=" ")
NDef("last_name", Or(
    "Blart", "Tralb"
))
NDef("name_suffix",
    Opt(NRef("seniority")),
    Or("Phd.", "CISSP", "MD.", "MBA", "NBA", "NFL", "WTF", "The Great"),
sep=" ")
NDef("seniority", Or(
    Or("Sr.", "Jr."),
    Ref("roman-numeral", cat=roman_numeral.TOP_CAT),
))
NDef("name_title", Or(
    "Sir", "Ms.", "Mr.", "Mrs.", "Senator", "Capt.", "Maj.", "Lt.", "President"
))
NDef("first_name", Or("Henry", "Susy"))
NDef("initial",
    String(min=1, max=2, charset=String.charset_alpha_upper), "."
)
