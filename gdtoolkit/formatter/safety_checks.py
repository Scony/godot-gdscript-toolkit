from typing import Optional
import difflib

from lark import Tree, Transformer, Token

from ..parser import parser
from .formatter import format_code
from .comments import gather_comments
from .expression_to_str import expression_to_str
from .exceptions import (
    TreeInvariantViolation,
    FormattingStabilityViolation,
    CommentPersistenceViolation,
)


class LoosenTreeTransformer(Transformer):
    def par_expr(self, args):  # pylint: disable=R0201
        return args[0] if len(args) > 0 else args

    def neg_expr(self, args):  # pylint: disable=R0201
        return (
            Token("NUMBER", "-{}".format(args[1].value))
            if isinstance(args[1], Token) and args[1].type == "NUMBER"
            else Tree("neg_expr", args)
        )

    def string(self, args):  # pylint: disable=R0201
        string_token = args[0]
        return expression_to_str(string_token)


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
        diff = "\n".join(
            difflib.unified_diff(
                str(given_code_parse_tree.pretty()).splitlines(),
                str(formatted_code_parse_tree.pretty()).splitlines(),
            )
        )
        raise TreeInvariantViolation(diff)


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
        diff = "\n".join(
            difflib.unified_diff(
                formatted_code.splitlines(), code_formatted_again.splitlines()
            )
        )
        raise FormattingStabilityViolation(diff)


# TODO: boost algorithm
def check_comment_persistence(
    given_code: str,
    formatted_code: str,
    given_code_comment_parse_tree: Optional[Tree] = None,
    formatted_code_comment_parse_tree: Optional[Tree] = None,
) -> None:
    original_comments = gather_comments(given_code, given_code_comment_parse_tree)
    comments_after_formatting = gather_comments(
        formatted_code, formatted_code_comment_parse_tree
    )
    for original_comment in original_comments:
        if not any(
            original_comment in comment_after_formatting
            for comment_after_formatting in comments_after_formatting
        ):
            raise CommentPersistenceViolation(original_comment)
