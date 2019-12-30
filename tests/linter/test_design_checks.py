import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
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
