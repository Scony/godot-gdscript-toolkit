import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
@pytest.mark.parametrize('code', [
"""
var x = _foo()
""",
"""
var x = self._foo()
""",
"""
var x = a.b.c.foo()
""",
])
def test_private_method_call_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
var x = y._foo()
""",
"""
var x = a.b.c._foo()
""",
])
def test_private_method_call_nok(code):
    simple_nok_check(code, 'private-method-call')


@pytest.mark.parametrize('code', [
"""
tool
extends Node
class_name Foo
enum { A, B, C }
const X = 1
signal s
export var k = 1
onready var y = null
var x = 1
onready var _y = null
var _x = 1
class Z:
    tool
    extends Node
func foo():
    pass
""",
])
def test_class_definitions_order_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""extends Node
tool
""",
"""tool;extends Node
tool
""",
"""
class X: extends Node;tool
""",
])
def test_class_definitions_order_nok(code):
    simple_nok_check(code, 'class-definitions-order')
