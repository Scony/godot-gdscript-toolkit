import pytest

from gdtoolkit.linter import lint_code, DEFAULT_CONFIG

from .common import simple_ok_check, simple_nok_check


# fmt: off
@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    else:
        return 'bar'
"""
    ],
)
def test_if_branch_returns_nok(code):
    simple_nok_check(code, "no-else-return", line=5)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    elif true:
        return 'bar'
    else:
        return 'foo'
"""
])
def test_elif_branch_returns_nok(code):
    outcome = lint_code(code, DEFAULT_CONFIG)
    assert len(outcome) == 2
    assert outcome[0].name == "no-elif-return"
    assert outcome[0].line == 5
    assert outcome[1].name == "no-else-return"
    assert outcome[1].line == 7


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    else:
        var x = 'bar'

    return x
"""
])
def test_else_branch_doesnt_returns_nok(code):
    simple_nok_check(code, "no-else-return", line=5)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    else:
        if true:
            return 'bar'
"""
])
def test_else_branch_with_nested_if_nok(code):
    simple_nok_check(code, "no-else-return", line=5)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        if true:
            return 'foo'
        else:
            return 'bar'
    else:
        return 'foo'
"""
])
def test_nested_ifs_nok(code):
    outcome = lint_code(code, DEFAULT_CONFIG)
    assert len(outcome) == 2
    assert outcome[0].name == "no-else-return"
    assert outcome[0].line == 6
    assert outcome[1].name == "no-else-return"
    assert outcome[1].line == 8


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        match x:
            1:
                return 'foo'
            _:
                return 'bar'
    else:
        return 'foo'
"""
])
def test_nested_match_nok(code):
    simple_nok_check(code, "no-else-return", line=9)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    elif true:
        var a = 'bar'
    else:
        return 'foo'
"""
])
def test_elif_branch_doesnt_return_nok(code):
    simple_nok_check(code, "no-elif-return", line=5)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    elif true:
        return 'bar'
    elif true:
        var a = 'foo'
    elif true:
        var a = 'bar'
    else:
        return 'foo'
"""
])
def test_elif_branch_returns_nok_2(code):
    outcome = lint_code(code, DEFAULT_CONFIG)
    assert len(outcome) == 2
    assert outcome[0].name == "no-elif-return"
    assert outcome[0].line == 5
    assert outcome[1].name == "no-elif-return"
    assert outcome[1].line == 7


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    return 'bar'
"""
])
def test_if_branch_returns_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    else:
        var x := 1
    var x := 2
"""
])
def test_var_avoids_error_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        if true:
            return 'foo'
    elif true:
        return 'bar'
    else:
        return 'foo'
"""
])
def test_nested_if_doesnt_always_returns_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        match x:
            1:
                return 'foo'
            _:
                var a = 'bar'
    else:
        return 'foo'
"""
"""
func foo():
    if true:
        match x:
            1:
                return 'foo'
            2:
                var a = 'bar'
            _:
                return 'foo'
    else:
        return 'bar'
"""
"""
func foo():
    if true:
        match x:
            1:
                return 'foo'
            2:
                return 'bar'
    else:
        return 'foo'
"""
])
def test_nested_match_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func foo():
    if true:
        return 'foo'
    if true:
        return 'bar'
"""
])
def test_doesnt_allow_elif_ok(code):
    simple_ok_check(code)
