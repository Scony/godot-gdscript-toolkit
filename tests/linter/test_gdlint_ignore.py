import pytest

from .common import simple_ok_check


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
def test_function_name_ok_when_ignored(code):
    simple_ok_check(code)
