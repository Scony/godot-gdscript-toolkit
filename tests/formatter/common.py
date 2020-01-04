from gdtoolkit.parser import parser
from gdtoolkit.formatter import format_code


def format_and_compare(input_code, expected_output_code):
    input_code_parse_tree = parser.parse(input_code)
    formatted_code = format_code(input_code, max_line_length=100)
    formatted_code_parse_tree = parser.parse(formatted_code)
    _invariant_check(input_code_parse_tree, formatted_code_parse_tree)
    _compare(formatted_code, expected_output_code)


def _invariant_check(input_code_parse_tree, formatted_code_parse_tree):
    """dummy function for better stack trace"""
    assert input_code_parse_tree == formatted_code_parse_tree


def _compare(formatted_code, expected_output_code):
    """dummy function for better stack trace"""
    assert formatted_code == expected_output_code
