import pytest

from .common import simple_ok_check, simple_nok_check


def test_max_file_lines_ok():
    code = "\n".join(["tool"] * 1000)
    simple_ok_check(code)


def test_max_file_lines_nok():
    code = "\n".join(["tool"] * 1001)
    simple_nok_check(code, "max-file-lines", 1001)


# fmt: off
@pytest.mark.parametrize('code', [
"""
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
""",
])
def test_max_line_length_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
""",
])
def test_max_line_length_nok(code):
    simple_nok_check(code, 'max-line-length')


@pytest.mark.parametrize('code', [
"""
func foo():
    var x


""",
"""
func foo():
    pass
""",
"""
func foo():
	x.bar()
""",
])
def test_trailing_ws_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""func foo():
    pass 
""",
"""func foo():
    pass   
""",
"""func foo():
    pass	
""",
"""func foo():
    pass 	  
""",
])
def test_trailing_ws_nok(code):
    simple_nok_check(code, 'trailing-whitespace')


@pytest.mark.parametrize('code', [
"""
func foo():
    pass
""",
"""
func foo():
	pass
""",
])
def test_mixed_tabs_and_spaces_ok(code):
    simple_ok_check(code)


@pytest.mark.parametrize('code', [
"""
class X:
    func foo():
    	pass
""",
"""
class X:
	func foo():
	    pass
""",
])
def test_mixed_tabs_and_spaces_nok(code):
    simple_nok_check(code, 'mixed-tabs-and-spaces', line=4)
