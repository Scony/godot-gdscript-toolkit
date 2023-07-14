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
"""# gdlint: disable=max-public-methods
func f0(): pass
func f1(): pass
func f2(): pass
func f3(): pass
func f4(): pass
func f5(): pass
func f6(): pass
func f7(): pass
func f8(): pass
func f9(): pass
func f10(): pass
func f11(): pass
func f12(): pass
func f13(): pass
func f14(): pass
func f15(): pass
func f16(): pass
func f17(): pass
func f18(): pass
func f19(): pass
func f20(): pass
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
