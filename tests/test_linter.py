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
