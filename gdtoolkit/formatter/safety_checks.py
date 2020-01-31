from typing import List

from ..parser import parser
from .formatter import format_code


class TreeInvariantViolation(Exception):
    pass


class FormattingStabilityViolation(Exception):
    pass


class CommentPersistenceViolation(Exception):
    pass


# TODO: modify formatted code parse tree inplace to enable tree modifications
def check_tree_invariant(given_code: str, formatted_code: str) -> None:
    given_code_parse_tree = parser.parse(given_code, loosen_grammar=True)
    formatted_code_parse_tree = parser.parse(formatted_code, loosen_grammar=True)
    if given_code_parse_tree != formatted_code_parse_tree:
        raise TreeInvariantViolation


def check_formatting_stability(formatted_code: str, max_line_length: int) -> None:
    code_formatted_again = format_code(formatted_code, max_line_length)
    if formatted_code != code_formatted_again:
        raise FormattingStabilityViolation


# TODO: gather comments using dedicated grammar & boost algorithm
def check_comment_persistence(given_code: str, formatted_code: str) -> None:
    original_comments = _gather_comments_from_code(given_code)
    comments_after_formatting = _gather_comments_from_code(formatted_code)
    for original_comment in original_comments:
        if not any(
            original_comment in comment_after_formatting
            for comment_after_formatting in comments_after_formatting
        ):
            raise CommentPersistenceViolation


def _gather_comments_from_code(gdscript_code: str) -> List[str]:
    lines = gdscript_code.splitlines()
    comments = []  # type: List[str]
    for line in lines:
        comment_start = line.find("#")
        if comment_start >= 0:
            comments.append(line[comment_start:])
    return comments
