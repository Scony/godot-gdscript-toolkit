import pytest

from .common import simple_ok_check, simple_nok_check


# fmt: off
@pytest.mark.parametrize('code', [
"""
func foo():
    var x
    x = 1
""",
"""
func foo():
    bar()
""",
"""
func foo():
    x.bar()
""",
"""
func foo():
    for x in [1]: break
""",
"""
func foo():
    for x in [1]: continue
""",
"""
func foo():
    '''docstr'''
"""
])
def test_expression_not_assigned_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""func foo():
    1 + 1
""",
"""func foo():
    true
""",
])
def test_expression_not_assigned_nok(code):
    simple_nok_check(code, 'expression-not-assigned')


@pytest.mark.parametrize('code', [
"""
func foo():
    pass
""",
"""
func foo():
    var x = true
    if x:
        pass
""",
])
def test_unnecessary_pass_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""func foo():
    pass
    1 + 1
""",
"""func foo():
    if x: pass; 1+1
""",
])
def test_unnecessary_pass_nok(code):
    simple_nok_check(code, 'unnecessary-pass', disable=['expression-not-assigned'])


@pytest.mark.parametrize('code', [
"""
const B = preload('b')
var A = load('a')
func foo():
    var X = load('c')
    var Y = preload('d')
""",
])
def test_duplicated_load_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
const B = preload('b')
var A = load('a')
func foo():
    var X = load('a')
""",
"""
const B = preload('b')
var A = load('a')
func foo():
    var X = preload('a')
""",
])
def test_duplicated_load_nok(code):
    simple_nok_check(code, 'duplicated-load', line=5)


@pytest.mark.parametrize('code', [
"""
func foo(x):
    print(x)
""",
"""
func foo(_x):
    pass
""",
])
def test_unused_argument_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func foo(x):
    pass
""",
])
def test_unused_argument_nok(code):
    simple_nok_check(code, 'unused-argument')
