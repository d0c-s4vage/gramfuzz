#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Defines the Python 2.7 grammar for gramfuzz. Note that although this
generates data that will pass the inital stages of python file parsing,
subsequent stages that require more specific logic than can be contained
within a grammar will fail.

E.g.:

    
"""


import gramfuzz
import gramfuzz.utils
import gramfuzz.errors
import gramfuzz.rand
from gramfuzz.fields import *


TOP_CAT = "python"


INDENT_LEVEL = 0
class INDENT(Field):
    def build(self, pre=None, shortest=False):
        global INDENT_LEVEL
        INDENT_LEVEL += 1
        # indent one extra time
        return "    "


class DEDENT(Field):
    def build(self, pre=None, shortest=False):
        global INDENT_LEVEL
        INDENT_LEVEL -= 1
        return NEWLINE().build(pre, shortest=shortest)


# hard-code the category for these classes
class PyDef(Def):
    cat = "py_def"
class PyRef(Ref):
    cat = "py_def"


class NEWLINE(Field):
    def build(self, pre=None, shortest=False):
        return "\n" + ("    " * INDENT_LEVEL)

# top level rule
Def("file_input",
    #STAR(Or(NEWLINE, PyRef("stmt"))),
    PLUS(PyRef("stmt")),
    cat = "python",
)

# reference rules
PyDef("decorator",
    "@", PyRef("dotted_name"), Opt("(", PyRef("arglist"), ")"), NEWLINE,
)
PyDef("decorators", PLUS(PyRef("decorator")))
PyDef("decorated",
    PyRef("decorators"), Or(PyRef("classdef"), PyRef("funcdef"))
)

PyDef("funcdef", "def ", PyRef("name"), PyRef("parameters"), ":", PyRef("suite"))
PyDef("parameters", "(", Opt(PyRef("varargslist")), ")")
PyDef("varargslist",
    STAR(PyRef("fpdef"), Opt("=", PyRef("test")), ", "),
    Or(
        Or(
            And("*", PyRef("name"), Opt(", ", "**", PyRef("name"))),
            And("**", PyRef("name"))
        ),
        And(PyRef("fpdef"), Opt("=", PyRef("test")), STAR(", ", PyRef("fpdef"), Opt("=", PyRef("test"))), Opt(", "))
    )
)
PyDef("fpdef",
    Or(
        PyRef("name"),
        And("(", PyRef("fplist"), ")")
    ),
)
PyDef("fplist",
    PyRef("fpdef"), STAR(", ", PyRef("fpdef")), Opt(", "),
)

PyDef("stmt", PyRef("simple_stmt") | PyRef("compound_stmt"))
PyDef("simple_stmt",
    PyRef("small_stmt"), STAR("; ", PyRef("small_stmt")), Opt(";"), NEWLINE
)
PyDef("small_stmt",
    Or(
        PyRef("pass_stmt"),
        PyRef("expr_stmt"),
        PyRef("print_stmt"),
        PyRef("del_stmt"),
        PyRef("flow_stmt"),
        PyRef("import_stmt"),
        PyRef("global_stmt"),
        PyRef("exec_stmt"),
        PyRef("assert_stmt"),
    )
)
PyDef("expr_stmt",
    PyRef("testlist"),
    Or(
        And(PyRef("augassign"), Or(PyRef("yield_expr"), PyRef("testlist"))),
        STAR("=", Or(PyRef("yield_expr"), PyRef("testlist")))
    )
)
PyDef("augassign", Or(
    " += ", " -= ", " *= ", " /= ", " %= ", " &= ", " |= ", " ^= ", " <<= ", " >>= ", " **= ", " //= "
))
PyDef("print_stmt",
    "print ", Or(
        And(PyRef("test"), STAR(", ", PyRef("test")), Opt(", ")),
        And(" >> ", PyRef("test"), Opt(PLUS(", ", PyRef("test")), Opt(", ")))
    )
)
PyDef("del_stmt", "del ", PyRef("exprlist"))
PyDef("pass_stmt", "pass")
PyDef("flow_stmt", Or(
    PyRef("break_stmt"),
    PyRef("continue_stmt"),
    PyRef("return_stmt"),
    PyRef("raise_stmt"),
    PyRef("yield_stmt"),
))
PyDef("break_stmt", "break")
PyDef("continue_stmt", "continue")
PyDef("return_stmt", "return ", Opt(PyRef("testlist")))
PyDef("yield_stmt", PyRef("yield_expr"))
PyDef("raise_stmt", "raise ", Opt(
    PyRef("test"), Opt(
        ", ", PyRef("test"), Opt(
            ", ", PyRef("test")
        )
    )
))
PyDef("import_stmt", Or(PyRef("import_name"), PyRef("import_from")))
PyDef("import_name", "import ", PyRef("dotted_as_names"))
PyDef("import_from",
    "from ", Or(And(STAR("."), PyRef("dotted_name")), PLUS(".")), " ",
    "import ", Or(" * ", And("(", PyRef("import_as_names"), ")"), PyRef("import_as_names"))
)
PyDef("import_as_name", PyRef("name"), Opt(" as ", PyRef("name")))
PyDef("dotted_as_name", PyRef("dotted_name"), Opt(" as ", PyRef("name")))
PyDef("import_as_names", PyRef("import_as_name"), STAR(", ", PyRef("import_as_name")), Opt(", "))
PyDef("dotted_as_names", PyRef("dotted_as_name"), STAR(", ", PyRef("dotted_as_name")))
PyDef("dotted_name", PyRef("name"), STAR(".", PyRef("name")))
PyDef("global_stmt", "global ", PyRef("name"), STAR(", ", PyRef("name")))
PyDef("exec_stmt", "exec ", PyRef("expr"), Opt("in ", PyRef("test"), Opt(", ", PyRef("test"))))
PyDef("assert_stmt", "assert ", PyRef("test"), Opt(", ", PyRef("test")))

PyDef("compound_stmt", Or(
    PyRef("if_stmt"),
    PyRef("while_stmt"),
    PyRef("for_stmt"),
    PyRef("try_stmt"),
    PyRef("with_stmt"),
    PyRef("funcdef"),
    PyRef("classdef"),
    PyRef("decorated"),
))
PyDef("if_stmt",
    "if ", PyRef("test"), ":", PyRef("suite"), STAR("elif ", PyRef("test"), ":", PyRef("suite")), Opt("else", ":", PyRef("suite"))
)
PyDef("while_stmt",
    "while ", PyRef("test"), ":", PyRef("suite"), Opt("else", ":", PyRef("suite"))
)
PyDef("for_stmt",
    "for ", PyRef("exprlist"), " in ", PyRef("testlist"), ":", PyRef("suite"), Opt("else", ":", PyRef("suite"))
)
PyDef("try_stmt",
    "try", ":", PyRef("suite"),
    Or(
        And(PLUS(PyRef("except_clause"), ":", PyRef("suite")), Opt("else", ":", PyRef("suite")), Opt("finally", ":", PyRef("suite"))),
        And("finally", ":", PyRef("suite"))
    )
)
PyDef("with_stmt",
    "with ", PyRef("with_item"), STAR(", ", PyRef("with_item")), ":", PyRef("suite")
)
PyDef("with_item", PyRef("test"), Opt(" as ", PyRef("expr")))
PyDef("except_clause", "except ", Opt(PyRef("test"), Or(" as ", ", "), PyRef("test")))
PyDef("suite", Or(
    PyRef("simple_stmt"),
    And(
        NEWLINE, INDENT, PLUS(PyRef("stmt")), DEDENT
    )
))

PyDef("testlist_safe",
    PyRef("old_test"), Opt(PLUS(", ", PyRef("old_test")), Opt(", "))
)
PyDef("old_test", PyRef("or_test") | PyRef("old_lambdef"))
PyDef("old_lambdef", "lambda ", Opt(PyRef("varargslist")), ": ", PyRef("old_test"))

PyDef("test", Or(
    And(PyRef("or_test"), Opt(" if ", PyRef("or_test"), " else ", PyRef("test"))),
    PyRef("lambdef")
))
PyDef("or_test",
    PyRef("and_test"), STAR(" or ", PyRef("and_test"))
)
PyDef("and_test",
    PyRef("not_test"), STAR(" and ", PyRef("not_test"))
)
PyDef("not_test",
    Or(
        And("not ", PyRef("not_test")),
        PyRef("comparison")
    )
)
PyDef("comparison",
    PyRef("expr"), STAR(PyRef("comp_op"), " ", PyRef("expr"))
)
PyDef("comp_op", Or(
    ' < ',' > ',' == ',' >= ',' <= ',' <> ',' != ',' in ', And(' not ',' in '),' is ',And(' is ',' not ')
))
PyDef("expr",
    PyRef("xor_expr"), STAR(" | ", PyRef("xor_expr"))
)
PyDef("xor_expr",
    PyRef("and_expr"), STAR(" ^ ", PyRef("and_expr"))
)
PyDef("and_expr",
    PyRef("shift_expr"), STAR(" & ", PyRef("shift_expr"))
)
PyDef("shift_expr",
    PyRef("arith_expr"), STAR(Or(" << ", " >> "), PyRef("arith_expr"))
)
PyDef("arith_expr",
    PyRef("term"), STAR(Or("+", "-"), PyRef("term"))
)
PyDef("term",
    PyRef("factor"), STAR(Or(" * "," / ", " % ", " // "), PyRef("factor"))
)
PyDef("factor",
    Or(
        And(Or("+", "-", "~"), PyRef("factor")),
        PyRef("power")
    )
)
PyDef("power",
    PyRef("atom"), " ", STAR(PyRef("trailer")), Opt(" ** ", PyRef("factor"))
)
PyDef("atom", Or(
    And("( ", Opt(PyRef("yield_expr"), PyRef("testlist_comp")), " )"),
    And("[ ", Opt(PyRef("listmaker")), " ] "),
    And("{ ", Opt(PyRef("dictorsetmaker")), " }"),
    And("` ", PyRef("testlist1"), " `"),
    PyRef("name"),
    PyRef("number"),
    PLUS(PyRef("string")),
))
PyDef("listmaker",
    PyRef("test"), Or(
        PyRef("list_for"),
        And(STAR(", ", PyRef("test")), Opt(", "))
    )
)
PyDef("testlist_comp",
    PyRef("test"), Or(
        PyRef("comp_for"),
        And(STAR(", ", PyRef("test")), Opt(", "))
    )
)
PyDef("lambdef",
    #"lambda ", Opt(PyRef("varargslist"), ": ", PyRef("test"))
    "lambda ", Opt(PyRef("varargslist")), ": ", PyRef("test")
)
PyDef("trailer", Or(
    And("( ", Opt(PyRef("arglist")), " )"),
    And("[ ", PyRef("subscriptlist"), " ]"),
    And(". ", PyRef("name"))
))
PyDef("subscriptlist",
    PyRef("subscript"), STAR(", ", PyRef("subscript")), Opt(", ")
)
PyDef("subscript", Or(
    And(".", ".", "."),
    PyRef("test"),
    And(Opt(PyRef("test")), ": ", PyRef("test"), PyRef("sliceop"))
))
PyDef("sliceop", ": ", Opt(PyRef("test")))
PyDef("exprlist", PyRef("expr"), STAR(", ", PyRef("expr")), Opt(", "))
PyDef("testlist", PyRef("test"), STAR(", ", PyRef("test")), Opt(", "))
PyDef("dictorsetmaker", Or(
    And(PyRef("test"), ": ", PyRef("test"), Or(
        PyRef("comp_for"),
        And(STAR(", ", PyRef("test"), ": ", PyRef("test")), Opt(", ")),
    )),
    And(PyRef("test"), Or(
        PyRef("comp_for"),
        And(STAR(", ", PyRef("test"), Opt(", ")))
    ))
))
PyDef("classdef",
    "class ", PyRef("name"), Opt("(", Opt(PyRef("testlist")), ")"), ":", PyRef("suite")
)
PyDef("arglist",
    STAR(PyRef("argument"), ", "), Or(
        And(PyRef("argument"), Opt(", ")),
        And("*", PyRef("test"), STAR(", ", PyRef("argument")), Opt(", ", "**", PyRef("test"))),
        And("**", PyRef("test"))
    )
)
PyDef("argument", Or(
    And(PyRef("test"), Opt(PyRef("comp_for"))),
    And(PyRef("test"), " = ", PyRef("test"))
))

PyDef("list_iter", PyRef("list_for") | PyRef("list_if"))
PyDef("list_for", "for ", PyRef("exprlist"), " in ", PyRef("testlist_safe"), Opt(PyRef("list_iter")))
PyDef("list_if", " if ", PyRef("old_test"), Opt(PyRef("list_iter")))

PyDef("comp_iter", PyRef("comp_for") | PyRef("comp_if"))
PyDef("comp_for", "for ", PyRef("exprlist"), " in ", PyRef("or_test"), Opt(PyRef("comp_iter")))
PyDef("comp_if", " if ", PyRef("old_test"), Opt(PyRef("comp_iter")))

PyDef("testlist1", PyRef("test"), STAR(", ", PyRef("test")))

PyDef("yield_expr", "yield ", Opt(PyRef("testlist")))



# ----------------


PyDef("number", Int)
PyDef("name", String(min=3, max=10))
PyDef("string", Q(String))
