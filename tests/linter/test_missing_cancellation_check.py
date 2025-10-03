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


# Tests for gdlint ignore comments
@pytest.mark.parametrize('code', [
"""
func test1(ct):
    await method1(ct)  # gdlint: ignore=missing-cancellation-check
""",
"""
func test2(ct):
    # gdlint: ignore=missing-cancellation-check
    await method2(ct)
""",
"""
# gdlint: disable=missing-cancellation-check
func test3(ct):
    await method3(ct)

func test4(ct):
    await method4(ct)
# gdlint: enable=missing-cancellation-check
""",
])
def test_missing_cancellation_check_with_ignore_comments(code):
    simple_ok_check(code, disable=["unused-argument", "missing-cancellation-token-argument"])