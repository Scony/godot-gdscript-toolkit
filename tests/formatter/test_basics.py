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


def test_indentation_using_tabs():
    input_code = "\n".join(
        [
            "extends Node",
            "func foo():",
            "  if True:",
            "    pass",
            "  if False:",
            "    while True:",
            "      pass",
        ]
    )
    expected_output_code = "\n".join(
        [
            "extends Node",
            "",
            "",
            "func foo():",
            "\tif True:",
            "\t\tpass",
            "\tif False:",
            "\t\twhile True:",
            "\t\t\tpass",
            "",
        ]
    )
    format_and_compare(input_code, expected_output_code)


def test_indentation_using_spaces():
    input_code = "\n".join(
        [
            "extends Node",
            "func foo():",
            "  if True:",
            "    pass",
            "  if False:",
            "    while True:",
            "      pass",
        ]
    )
    expected_output_code = "\n".join(
        [
            "extends Node",
            "",
            "",
            "func foo():",
            "   if True:",
            "      pass",
            "   if False:",
            "      while True:",
            "         pass",
            "",
        ]
    )
    format_and_compare(input_code, expected_output_code, spaces_for_indent=3)
