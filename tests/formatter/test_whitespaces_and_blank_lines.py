import pytest

from .common import format_and_compare


# fmt: off
@pytest.mark.parametrize("input_code,expected_output_code", [
(
"""

class X:

    func foo():

        # aaa
        pass  # bbb
        # ccc
        
    


""",
"""class X:
    func foo():
        # aaa
        pass  # bbb
        # ccc
""",
),
])
# fmt: on
def test_formatting(input_code, expected_output_code):
    format_and_compare(input_code, expected_output_code)
