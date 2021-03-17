import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
@pytest.mark.parametrize('code', [
"""
# gdlint: ignore=function-name
func some_Button_pressed():
    pass
""",
"""
# gdlint:ignore = function-name
func SomeName():
    pass
""",
"""
# gdlint:ignore = function-name, function-argument-name
func SomeName(someArg):
    assert(someArg > 0)
""",
"""
# gdlint:ignore = function-name , function-argument-name
func SomeName(someArg):
    assert(someArg > 0)
""",
"""
# gdlint:ignore = function-name ,function-argument-name
func SomeName(someArg):
    assert(someArg > 0)
""",
])
def test_linting_ok_when_problem_ignored(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
# gdlint: disable=function-name
func some_Button_pressed():
    pass
""",
])
def test_linting_ok_when_problem_disabled(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
# gdlint: disable=function-name
func some_Button_pressed():
    pass
# gdlint: enable=function-name
func some_Button_pressed():
    pass
""",
])
def test_linting_nok_when_problem_enabled_again(code):
    simple_nok_check(code, check_name='function-name', line=6)
