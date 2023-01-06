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
