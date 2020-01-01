import pytest

from gdtoolkit.parser import parser
from gdtoolkit.formatter import format_code


@pytest.mark.parametrize("input_code,expected_output_code", [("", ""),])
def test_formatting(input_code, expected_output_code):
    input_code_parse_tree = parser.parse(input_code)
    formatted_code = format_code(input_code, 100)
    formatted_code_parse_tree = parser.parse(formatted_code)
    assert input_code_parse_tree == formatted_code_parse_tree
    assert formatted_code == expected_output_code
