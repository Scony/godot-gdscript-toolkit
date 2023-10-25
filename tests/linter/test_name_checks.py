import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
@pytest.mark.parametrize('code', [
"""
func foo():
    pass
""",
"""
func foo_bar():
    pass
""",
"""
func _foo():
    pass
""",
"""
func _foo_bar():
    pass
""",
"""
func _on_Button_pressed():
    pass
""",
])
def test_function_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func some_Button_pressed():
    pass
""",
"""
func SomeName():
    pass
""",
])
def test_function_name_nok(code):
    simple_nok_check(code, 'function-name')


@pytest.mark.parametrize('code', [
"""
class_name SomeClassName
""",
"""
class_name Some
""",
])
def test_class_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
class_name some_class_name
""",
"""
class_name _Some
""",
])
def test_class_name_nok(code):
    simple_nok_check(code, 'class-name')


@pytest.mark.parametrize('code', [
"""
class _SubClassName:
    pass
""",
"""
class SubClassName:
    pass
""",
])
def test_sub_class_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
class SubClassName_:
    pass
""",
"""
class sub_class_name:
    pass
""",
])
def test_sub_class_name_nok(code):
    simple_nok_check(code, 'sub-class-name')


@pytest.mark.parametrize('code', [
"""
signal some_signal
""",
"""
signal signal(a, b, c)
""",
])
def test_signal_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
signal someSignal
""",
"""
signal Signal(a, b)
""",
])
def test_signal_name_nok(code):
    simple_nok_check(code, 'signal-name')


@pytest.mark.parametrize('code', [
"""
enum Name {}
""",
"""
enum PascalCase { XXX }
""",
"""
enum PascalXCase { XXX }
""",
])
def test_enum_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
enum some_name {}
""",
"""
enum camelCase { XXX }
""",
"""
enum PascalCase_ { XXX }
""",
])
def test_enum_name_nok(code):
    simple_nok_check(code, 'enum-name')


@pytest.mark.parametrize('code', [
"""
enum Name { XXX }
""",
"""
enum { XXX, Y_Y_Y }
""",
])
def test_enum_element_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
enum { X_, Y }
""",
"""
enum { _XXX }
""",
"""
enum { xx_xx }
""",
"""
enum { SomeStuff }
""",
])
def test_enum_element_name_nok(code):
    simple_nok_check(code, 'enum-element-name')


@pytest.mark.parametrize('code', [
"""func foo():
    for _x in y:
        pass
""",
"""func foo():
    for xyz in y:
        pass
""",
"""func foo():
    for aaa_bbb in y:
        pass
""",
"""func foo():
    for _x: int in y:
        pass
""",
"""func foo():
    for xyz: int in y:
        pass
""",
"""func foo():
    for aaa_bbb: int in y:
        pass
""",
])
def test_loop_variable_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""func foo():
    for x_ in y:
        pass
""",
"""func foo():
    for xX in y:
        pass
""",
"""func foo():
    for X_X in y:
        pass
""",
"""func foo():
    for x_: int in y:
        pass
""",
"""func foo():
    for xX: int in y:
        pass
""",
"""func foo():
    for X_X: int in y:
        pass
""",
])
def test_loop_variable_name_nok(code):
    simple_nok_check(code, 'loop-variable-name')


@pytest.mark.parametrize('code', [
"""
func foo(a, _b, c_d := 123, xxx : int):
    pass
""",
])
def test_function_argument_name_ok(code):
    simple_ok_check(code, disable=['unused-argument'])


@pytest.mark.parametrize('code', [
"""
func foo(a_):
    pass
""",
"""
func foo(xX):
    pass
""",
"""
func foo(X_X):
    pass
""",
])
def test_function_argument_name_nok(code):
    simple_nok_check(code, 'function-argument-name', disable=['unused-argument'])


@pytest.mark.parametrize('code', [
"""
func foo():
    var xxx
""",
"""
func foo():
    var x_y = 1
""",
"""
func foo():
    var y : int = 1
""",
"""
func foo():
    var y := 1
""",
"""
func foo():
    var y : int
""",
])
def test_function_variable_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""func foo():
    var xxx_
""",
"""func foo():
    var _x_y = 1
""",
"""func foo():
    var X : int = 1
""",
"""func foo():
    var yY := 1
""",
])
def test_function_variable_name_nok(code):
    simple_nok_check(code, 'function-variable-name')


@pytest.mark.parametrize('code', [
"""
func foo():
    var XxxYyy = preload()
""",
])
def test_function_preload_variable_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""func foo():
    var x_y = preload()
""",
])
def test_function_preload_variable_name_nok(code):
    simple_nok_check(code, 'function-preload-variable-name')


@pytest.mark.parametrize('code', [
"""
const X = 1
""",
"""
const _X = 2
""",
"""
const X_Y_Z = 2
""",
])
def test_constant_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
const Xx = 1
""",
"""
const x_x = 2
""",
])
def test_constant_name_nok(code):
    simple_nok_check(code, 'constant-name')


@pytest.mark.parametrize('code', [
"""
const Xx = load()
""",
"""
const XxYy = preload()
""",
"""
const X = load()
""",
"""
const X_Y_Z = preload()
""",
])
def test_load_constant_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
const _Xx = preload()
""",
"""
const x_x = load()
""",
])
def test_load_constant_name_nok(code):
    simple_nok_check(code, 'load-constant-name')


@pytest.mark.parametrize('code', [
"""
var x
""",
"""
var xx_yy : int
""",
"""
var _xx_yy := 1.3
""",
])
def test_class_variable_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
var X_Y
""",
"""
var x_
""",
"""
var Xx
""",
"""
var XY_Z
""",
])
def test_class_variable_name_nok(code):
    simple_nok_check(code, 'class-variable-name')


@pytest.mark.parametrize('code', [
"""
var x = load()
""",
"""
var xx_yy = preload()
""",
"""
var _xx_yy := load()
""",
"""
var XxYy := load()
""",
])
def test_class_load_variable_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
var X_Y = load()
""",
"""
var x_ = load()
""",
"""
var XY_Z = load()
""",
])
def test_class_load_variable_name_nok(code):
    simple_nok_check(code, 'class-load-variable-name')
