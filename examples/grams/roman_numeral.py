#!/usr/bin/env python
# -*- coding: utf-8 -*-


from gramfuzz.fields import *


TOP_CAT = "roman-numeral"


# roman-numeral BNF grammar taken from
# https://stackoverflow.com/questions/14897872/prolog-roman-numerals-attribute-grammars
#
#        <roman> ::= <hundreds> <tens> <units>
#     <hundreds> ::= <low hundreds> | CD | D <low hundreds> | CM
# <low hundreds> ::= e | <low hundreds> C
#         <tens> ::= <low tens> | XL | L <low tens> | XC
#     <low tens> ::= e | <low tens> X
#        <units> ::= <low units> | IV | V <low units> | IX
#    <low units> ::= e | <low units> I
#


class RDef(Def): cat="roman-numeral-def"
class RRef(Ref): cat="roman-numeral-def"


# top-level rule
Def("roman-numeral",
    RRef("hundreds"), RRef("tens"), RRef("units"),
cat="roman-numeral")


# helper rules
RDef("hundreds",
    RRef("low-hundreds") | "CD" | And("D", RRef("low-hundreds")) | "CM"
)
RDef("low-hundreds",
    And(RRef("low-hundreds"), "C") | ""
)
RDef("tens",
    RRef("low-tens") | "XL" | And("L", RRef("low-tens")) | "XC"
)
RDef("low-tens",
    And(RRef("low-tens"), "X") | ""
)
RDef("units",
    RRef("low-units") | "IV" | And("V", RRef("low-units") | "IX")
)
RDef("low-units",
    And(RRef("low-units"), "I") | ""
)
