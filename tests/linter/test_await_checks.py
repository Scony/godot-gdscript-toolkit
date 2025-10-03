import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
@pytest.mark.parametrize('code', [
"""
func foo(ct):
    await get_tree().process_frame
    if ct.is_cancelled():
        return
    print("ok")
""",
"""
func bar(cancellation_token):
    await some_coroutine()
    if cancellation_token.is_cancelled():
        return
""",
"""
func baz(ct):
    var x = 1
    await delayed_operation()
    if ct.is_cancelled():
        return
    await another_operation()
    if ct.is_cancelled():
        return
""",
])
def test_missing_cancellation_check_ok(code):
    simple_ok_check(code, disable=["unused-argument", "missing-cancellation-token-argument"])


@pytest.mark.parametrize('code,line', [
("""
func foo(ct):
    await get_tree().process_frame
    print("missing check")
""", 3),
("""
func bar(ct):
    await some_coroutine()
""", 3),
("""
func baz(ct):
    await operation1()
    if ct.is_cancelled():
        return
    await operation2()
    print("missing check after second await")
""", 6),
])
def test_missing_cancellation_check_nok(code, line):
    simple_nok_check(code, "missing-cancellation-check", line=line, disable=["unused-argument", "missing-cancellation-token-argument"])


# Tests for missing-cancellation-token-argument
@pytest.mark.parametrize('code', [
"""
func foo(ct):
    await async_method(ct)
    if ct.is_cancelled():
        return
""",
"""
func bar(cancellation_token):
    await load_data(123, cancellation_token)
    if cancellation_token.is_cancelled():
        return
""",
"""
func baz(ct):
    await operation1(ct)
    if ct.is_cancelled():
        return
    await operation2(arg1, arg2, ct)
    if ct.is_cancelled():
        return
""",
"""
func no_ct():
    await some_method()
""",
])
def test_missing_cancellation_token_argument_ok(code):
    simple_ok_check(code, disable=["unused-argument", "missing-cancellation-check"])


@pytest.mark.parametrize('code,line', [
("""
func foo(ct):
    await async_method()
""", 3),
("""
func bar(cancellation_token):
    await load_data(123)
""", 3),
("""
func baz(ct):
    await operation1(ct)
    await operation2()
""", 4),
])
def test_missing_cancellation_token_argument_nok(code, line):
    simple_nok_check(code, "missing-cancellation-token-argument", line=line, disable=["unused-argument", "missing-cancellation-check"])