import os

import pytest
import hypothesis.extra.lark
from hypothesis import settings, given, HealthCheck
from lark import Lark

from gdtoolkit.parser import parser


with open("gdtoolkit/parser/gdscript.lark", "r") as fh:
    gdscript_grammar = fh.read()
    simplified_gdscript_grammar = gdscript_grammar.replace(".2", "")
    gdscript_lark = Lark(simplified_gdscript_grammar)


@pytest.mark.generated
@settings(
    deadline=None,
    suppress_health_check=(HealthCheck.filter_too_much,),
    max_examples=500,
)
@given(hypothesis.extra.lark.from_lark(gdscript_lark, start="expr"))
def test_expression_parsing(expression):
    gdscript_code = "func foo():\n\t{}".format(expression)
    parser.parse(gdscript_code)  # just checking if not throwing
