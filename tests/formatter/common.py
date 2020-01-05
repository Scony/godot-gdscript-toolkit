from gdtoolkit.parser import parser
from gdtoolkit.formatter import format_code


def format_and_compare(input_code, expected_output_code):
    input_code_parse_tree = parser.parse(input_code)
    formatted_code = format_code(input_code, max_line_length=100)
    formatted_code_parse_tree = parser.parse(formatted_code)
    _invariant_check(input_code_parse_tree, formatted_code_parse_tree)
    _compare(formatted_code, expected_output_code)
    input_code_comments = _gather_comment_statistics_from_code(input_code)
    formatted_code_comments = _gather_comment_statistics_from_code(formatted_code)
    _comment_preservation_check(input_code_comments, formatted_code_comments)


def _invariant_check(input_code_parse_tree, formatted_code_parse_tree):
    """dummy function for better stack trace"""
    assert input_code_parse_tree == formatted_code_parse_tree


def _compare(formatted_code, expected_output_code):
    """dummy function for better stack trace"""
    assert formatted_code == expected_output_code


def _comment_preservation_check(input_code_comments, formatted_code_comments):
    """dummy function for better stack trace"""
    assert input_code_comments == formatted_code_comments


def _gather_comment_statistics_from_code(gdscript_code: str) -> dict:
    stats = {}
    lines = gdscript_code.splitlines()
    for line in lines:
        comment_start = line.find("#")
        if comment_start >= 0:
            comment = line[comment_start:]
            stats[comment] = stats.get(comment, 0) + 1
    return stats
