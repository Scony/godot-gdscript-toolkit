from typing import Optional

from lark import Tree, Transformer

from ..parser import parser
from .formatter import format_code
from .comments import gather_comments_from_code


class TreeInvariantViolation(Exception):
    pass


class FormattingStabilityViolation(Exception):
    pass


class CommentPersistenceViolation(Exception):
    pass


class LoosenTreeTransformer(Transformer):
    def par_expr(self, args):  # pylint: disable=R0201
        return args[0] if len(args) > 0 else args


def check_tree_invariant(
    given_code: str,
    formatted_code: str,
    given_code_parse_tree: Optional[Tree] = None,
    formatted_code_parse_tree: Optional[Tree] = None,
) -> None:
    given_code_parse_tree = (
        given_code_parse_tree
        if given_code_parse_tree is not None
        else parser.parse(given_code)
    )
    formatted_code_parse_tree = (
        formatted_code_parse_tree
        if formatted_code_parse_tree is not None
        else parser.parse(formatted_code)
    )
    loosen_tree_transformer = LoosenTreeTransformer()
    given_code_parse_tree = loosen_tree_transformer.transform(given_code_parse_tree)
    formatted_code_parse_tree = loosen_tree_transformer.transform(
        formatted_code_parse_tree
    )
    if given_code_parse_tree != formatted_code_parse_tree:
        raise TreeInvariantViolation


def check_formatting_stability(
    formatted_code: str,
    max_line_length: int,
    parse_tree: Optional[Tree] = None,
    comment_parse_tree: Optional[Tree] = None,
) -> None:
    code_formatted_again = format_code(
        formatted_code,
        max_line_length,
        parse_tree=parse_tree,
        comment_parse_tree=comment_parse_tree,
    )
    if formatted_code != code_formatted_again:
        raise FormattingStabilityViolation


# TODO: boost algorithm
def check_comment_persistence(
    given_code: str,
    formatted_code: str,
    given_code_comment_parse_tree: Optional[Tree] = None,
    formatted_code_comment_parse_tree: Optional[Tree] = None,
) -> None:
    original_comments = gather_comments_from_code(
        given_code, comment_tree=given_code_comment_parse_tree,
    )
    comments_after_formatting = gather_comments_from_code(
        formatted_code, comment_tree=formatted_code_comment_parse_tree,
    )
    for original_comment in original_comments:
        if not any(
            original_comment in comment_after_formatting
            for comment_after_formatting in comments_after_formatting
        ):
            raise CommentPersistenceViolation
