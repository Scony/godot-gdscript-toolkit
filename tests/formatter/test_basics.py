import pytest

from .common import format_and_compare


# fmt: off
@pytest.mark.parametrize("input_code,expected_output_code", [
("", ""),
(
"pass",
"""pass
""",
),
])
# fmt: on
def test_formatting(input_code, expected_output_code):
    format_and_compare(input_code, expected_output_code)
