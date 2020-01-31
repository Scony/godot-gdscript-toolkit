from typing import List
import difflib

from gdtoolkit.parser import parser
from gdtoolkit.formatter import format_code


MAX_LINE_LENGTH = 100


def format_with_checks(
    input_code,
    check_comment_persistence=False,
    check_tree_invariant=False,
    check_formatting_stability=False,
):
    formatted_code = format_code(input_code, max_line_length=MAX_LINE_LENGTH)

    if check_comment_persistence:
        input_code_comment_stats = _gather_comment_statistics_from_code(input_code)
        formatted_code_comments = _gather_comments_from_code(formatted_code)
        _comment_preservation_check(input_code_comment_stats, formatted_code_comments)

    if check_tree_invariant:
        _tree_invariant_check(input_code, formatted_code)

    if check_formatting_stability:
        code_formatted_again = format_code(
            formatted_code, max_line_length=MAX_LINE_LENGTH
        )
        _compare_again(code_formatted_again, formatted_code)


def format_and_compare(input_code, expected_output_code):
    formatted_code = format_code(input_code, max_line_length=MAX_LINE_LENGTH)
    _compare(formatted_code, expected_output_code)

    code_formatted_again = format_code(formatted_code, max_line_length=MAX_LINE_LENGTH)
    _compare_again(code_formatted_again, formatted_code)

    _tree_invariant_check(input_code, formatted_code)

    input_code_comment_stats = _gather_comment_statistics_from_code(input_code)
    formatted_code_comments = _gather_comments_from_code(formatted_code)
    _comment_preservation_check(input_code_comment_stats, formatted_code_comments)


def _tree_invariant_check(input_code, formatted_code):
    input_code_parse_tree = parser.parse(input_code, loosen_grammar=True)
    formatted_code_parse_tree = parser.parse(formatted_code, loosen_grammar=True)
    diff = "\n".join(
        difflib.unified_diff(
            str(input_code_parse_tree.pretty()).splitlines(),
            str(formatted_code_parse_tree.pretty()).splitlines(),
        )
    )
    assert input_code_parse_tree == formatted_code_parse_tree, diff


def _compare(formatted_code, expected_output_code):
    diff = "\n".join(
        difflib.unified_diff(
            expected_output_code.splitlines(), formatted_code.splitlines()
        )
    )
    assert formatted_code == expected_output_code, diff


_compare_again = _compare


def _comment_preservation_check(
    input_code_comment_stats: dict, formatted_code_comments: List[str]
):
    for input_comment, occurances_in_input in input_code_comment_stats.items():
        occurances_in_output = 0
        for formatted_comment in formatted_code_comments:
            if input_comment in formatted_comment:
                occurances_in_output += 1
        assert occurances_in_input <= occurances_in_output


def _gather_comment_statistics_from_code(gdscript_code: str) -> dict:
    stats = {}  # type: dict
    lines = gdscript_code.splitlines()
    for line in lines:
        comment_start = line.find("#")
        if comment_start >= 0:
            comment = line[comment_start:]
            stats[comment] = stats.get(comment, 0) + 1
    return stats


def _gather_comments_from_code(gdscript_code: str) -> List[str]:
    lines = gdscript_code.splitlines()
    comments = []  # type: List[str]
    for line in lines:
        comment_start = line.find("#")
        if comment_start >= 0:
            comments.append(line[comment_start:])
    return comments
