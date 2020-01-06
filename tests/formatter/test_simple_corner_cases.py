import pytest

from .common import format_and_compare


# fmt: off
@pytest.mark.parametrize("input_code,expected_output_code", [
(
"""tool;tool;tool # xxx""",
"""tool
tool
tool  # xxx
""",
),
(
"""tool
class X: # aaa
    func foo(): # bbb
        pass
""",
"""tool
class X:  # aaa
    func foo():  # bbb
        pass
""",
),
])
# fmt: on
def test_formatting(input_code, expected_output_code):
    format_and_compare(input_code, expected_output_code)
