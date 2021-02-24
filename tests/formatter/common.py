import difflib

from gdtoolkit.formatter import format_code, check_formatting_safety


MAX_LINE_LENGTH = 100


def format_and_compare(input_code, expected_output_code):
    formatted_code = format_code(input_code, max_line_length=MAX_LINE_LENGTH)
    _compare(formatted_code, expected_output_code)
    check_formatting_safety(input_code, formatted_code, MAX_LINE_LENGTH)


def _compare(formatted_code, expected_output_code):
    diff = "\n".join(
        difflib.unified_diff(
            expected_output_code.splitlines(), formatted_code.splitlines()
        )
    )
    assert formatted_code == expected_output_code, diff
