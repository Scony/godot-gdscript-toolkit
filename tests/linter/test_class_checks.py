import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
@pytest.mark.parametrize('code', [
"""
pass
class_name Foo
extends Node
"docstring"
signal s
enum { A, B, C }
const X = 1
static var sx
@export_group("Foo")
@export var k = 1
var x = 1
var _x = 1
@onready var y = null
@onready var _y = null
class Z:
    pass
    extends Node
func foo():
    pass
""",
])
def test_class_definitions_order_ok(code):
    simple_ok_check(code, disable="unnecessary-pass")


@pytest.mark.parametrize('code', [
"""var x
signal s
""",
"""extends Node;var x
signal s
""",
"""
class X: var x;extends Node
""",
"""var _x
var x
""",
"""@onready var x
var y
""",
"""@onready var _x
@onready var x
""",
"""var x
enum X { A, B }
""",
"""var x
class_name Asdf
""",
"""var x
const X = 1
""",
"""var x
@tool
""",
"""static func foo(): pass
var x
""",
"""'docstring'
extends Node
""",
])
def test_class_definitions_order_nok(code):
    simple_nok_check(code, 'class-definitions-order')
