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
    simple_ok_check(code, disable=['unused-argument'])


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
    simple_nok_check(code, 'function-arguments-number', disable=['unused-argument'])


@pytest.mark.parametrize('code', [
"""
func foo1():
    pass
func foo2():
    pass
func foo3():
    pass
func foo4():
    pass
func foo5():
    pass
func foo6():
    pass
func foo7():
    pass
func foo8():
    pass
func foo9():
    pass
func foo10():
    pass
func foo11():
    pass
class X:
    func foo1():
        pass
    func foo2():
        pass
    func foo3():
        pass
    func foo4():
        pass
    func foo5():
        pass
    func foo6():
        pass
    func foo7():
        pass
    func foo8():
        pass
    func foo9():
        pass
    func foo10():
        pass
    func foo11():
        pass
""",
])
def test_max_public_methods_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
func foo1():
    pass
func foo2():
    pass
func foo3():
    pass
func foo4():
    pass
func foo5():
    pass
func foo6():
    pass
func foo7():
    pass
func foo8():
    pass
func foo9():
    pass
func foo10():
    pass
func foo11():
    pass
func foo12():
    pass
func foo13():
    pass
func foo14():
    pass
func foo15():
    pass
func foo16():
    pass
func foo17():
    pass
func foo18():
    pass
func foo19():
    pass
func foo20():
    pass
func foo21():
    pass
""",
])
def test_max_public_methods_nok(code):
    simple_nok_check(code, 'max-public-methods', line=1)


@pytest.mark.parametrize('code', [
"""
func foo():
    if 1 > 2:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
""",
"""
func foo():
    if 1 > 2:
        if 1:
            if 1:
                if 1:
                    return 1
                return 1
            return 1
        elif 1:
            return 1
        return 1
""",
])
def test_max_returns_ok(code):
    simple_ok_check(code, disable=["no-elif-return"])


@pytest.mark.parametrize('code', [
"""
func foo():
    if 1 > 2:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
    elif 1:
        return 1
    return 1
""",
"""
func foo():
    if 1 > 2:
        if 1:
            if 1:
                if 1:
                    return 1
                return 1
            return 1
        elif 1:
            return 1
        return 1
        return 1

    return 1
""",
])
def test_max_returns_nok(code):
    simple_nok_check(code, 'max-returns', line=15, disable=['no-elif-return'])
