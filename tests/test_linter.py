import pytest

from gdtoolkit.linter import lint_code


def test_empty_code_linting():
    lint_code('')


def test_function_name():       # TODO: ok case
    code = """
func SomeName():
    pass
"""
    outcome = lint_code(code)
    assert len(outcome) == 1
    assert outcome[0].name == 'function-name'
    assert outcome[0].line == 2


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
    outcome = lint_code(code)
    assert len(outcome) == 0


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
    outcome = lint_code(code)
    assert len(outcome) == 1
    assert outcome[0].name == 'function-arguments-number'
    assert outcome[0].line == 2


@pytest.mark.parametrize('code', [
"""
class_name SomeClassName
""",
"""
class SubClassName:
    tool
""",
])
def test_class_name_ok(code):
    outcome = lint_code(code)
    assert len(outcome) == 0


@pytest.mark.parametrize('code', [
"""
class_name some_class_name
""",
"""
class sub_class_name:
    tool
""",
])
def test_class_name_nok(code):
    outcome = lint_code(code)
    assert len(outcome) == 1
    assert outcome[0].name == 'class-name'
    assert outcome[0].line == 2


@pytest.mark.parametrize('code', [
"""
signal some_signal
""",
"""
signal signal(a, b, c)
""",
])
def test_signal_name_ok(code):
    outcome = lint_code(code)
    assert len(outcome) == 0


@pytest.mark.parametrize('code', [
"""
signal someSignal
""",
"""
signal Signal(a, b)
""",
])
def test_signal_name_nok(code):
    outcome = lint_code(code)
    assert len(outcome) == 1
    assert outcome[0].name == 'signal-name'
    assert outcome[0].line == 2
