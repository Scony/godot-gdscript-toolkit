import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
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


# Tests for gdlint ignore comments
@pytest.mark.parametrize('code', [
"""
func test1(ct):
    # gdlint: ignore=missing-cancellation-token-argument
    await some_method()
    if ct.is_cancelled():
        return
""",
"""
func test2(ct):
    await some_method()  # gdlint: ignore=missing-cancellation-token-argument
    if ct.is_cancelled():
        return
""",
"""
# gdlint: disable=missing-cancellation-token-argument
func test3(ct):
    await some_method()
    if ct.is_cancelled():
        return
# gdlint: enable=missing-cancellation-token-argument
""",
])
def test_missing_cancellation_token_argument_with_ignore_comments(code):
    simple_ok_check(code, disable=["unused-argument", "missing-cancellation-check"])
