import pytest

from gdtoolkit.linter import lint_code, DEFAULT_CONFIG


def simple_ok_check(code):
    outcome = lint_code(code)
    assert len(outcome) == 0


def simple_nok_check(code, check_name):
    config_w_disable = DEFAULT_CONFIG.copy()
    config_w_disable.update({'disable':[check_name]})
    assert len(lint_code(code, config_w_disable)) == 0

    outcome = lint_code(code)
    assert len(outcome) == 1
    assert outcome[0].name == check_name
    assert outcome[0].line == 2


def test_empty_code_linting():
    lint_code('')


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
func foo(a1:int,a2:int):
    pass
""",
"""
func foo(a1,a2):
    pass
""",
"""
func foo():
    pass
""",
"""
func foo() -> int:
    pass
""",
])
def test_function_args_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func foo(a1:int,a2:int,a3:int,a4:int,a5:int,a6:int,a7:int,a8:int,a9:int,a10:int,a11:int):
    pass
""",
"""
func foo(a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11):
    pass
""",
])
def test_function_args_nok(code):
    simple_nok_check(code, 'function-arguments-number')


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
    tool
""",
"""
class SubClassName:
    tool
""",
])
def test_sub_class_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
class SubClassName_:
    tool
""",
"""
class sub_class_name:
    tool
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
    simple_ok_check(code)


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
    simple_nok_check(code, 'function-argument-name')


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
    var Xxx = load()
""",
"""
func foo():
    var XxxYyy = preload()
""",
])
def test_function_load_variable_name_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""func foo():
    var xxx = load()
""",
"""func foo():
    var x_y = preload()
""",
])
def test_function_load_variable_name_nok(code):
    simple_nok_check(code, 'function-load-variable-name')
