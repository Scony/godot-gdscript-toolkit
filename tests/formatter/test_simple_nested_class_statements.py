import pytest

from .common import format_and_compare


# fmt: off
@pytest.mark.parametrize("input_code,expected_output_code", [
(
"""tool
class X:
    tool
""",
"""tool
class X:
    tool
""",
),
(
"""tool
tool
class X:
    tool
    tool
""",
"""tool
tool
class X:
    tool
    tool
""",
),
(
"""tool
tool
class X:
    tool    # xxx
    tool
""",
"""tool
tool
class X:
    tool  # xxx
    tool
""",
),
(
"""tool
tool
class X:
    tool    # xxx


    tool
""",
"""tool
tool
class X:
    tool  # xxx


    tool
""",
),
(
"""tool
class X:
    tool
    class Y:
        tool
""",
"""tool
class X:
    tool
    class Y:
        tool
""",
),
(
"""tool
class X:
    # aaa
    tool
""",
"""tool
class X:
    # aaa
    tool
""",
),
(
"""tool
class X:
    # aaa
    tool
    # bbb
""",
"""tool
class X:
    # aaa
    tool
    # bbb
""",
),
])
# fmt: on
def test_formatting(input_code, expected_output_code):
    format_and_compare(input_code, expected_output_code)
