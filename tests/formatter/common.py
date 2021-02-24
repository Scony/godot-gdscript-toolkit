from typing import List
import difflib

from gdtoolkit.parser import parser
from gdtoolkit.formatter import format_code, LoosenTreeTransformer
from gdtoolkit.formatter.safety_checks import check_comment_persistence


MAX_LINE_LENGTH = 100


def format_with_checks(input_code: str):
    formatted_code = format_code(input_code, max_line_length=MAX_LINE_LENGTH)

    check_comment_persistence(input_code, formatted_code)
    _tree_invariant_check(input_code, formatted_code)

    # check_formatting_stability:
    code_formatted_again = format_code(formatted_code, max_line_length=MAX_LINE_LENGTH)
    _compare_again(code_formatted_again, formatted_code)


def format_and_compare(input_code, expected_output_code):
    formatted_code = format_code(input_code, max_line_length=MAX_LINE_LENGTH)
    _compare(formatted_code, expected_output_code)

    code_formatted_again = format_code(formatted_code, max_line_length=MAX_LINE_LENGTH)
    _compare_again(code_formatted_again, formatted_code)

    _tree_invariant_check(input_code, formatted_code)

    check_comment_persistence(input_code, formatted_code)


def _tree_invariant_check(input_code, formatted_code):
    input_code_parse_tree = parser.parse(input_code)
    formatted_code_parse_tree = parser.parse(formatted_code)
    loosen_tree_transformer = LoosenTreeTransformer()
    input_code_parse_tree = loosen_tree_transformer.transform(input_code_parse_tree)
    formatted_code_parse_tree = loosen_tree_transformer.transform(
        formatted_code_parse_tree
    )
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
