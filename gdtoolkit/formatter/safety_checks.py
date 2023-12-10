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


# pylint: disable-next=too-many-public-methods
class LoosenTreeTransformer(Transformer):
    def par_expr(self, args):
        return args[0] if len(args) > 0 else args

    def asless_actual_neg_expr(self, args):
        return (
            Token("NUMBER", f"-{args[1].value}")
            if isinstance(args[1], Token) and args[1].type == "NUMBER"
            else Tree("asless_actual_neg_expr", args)
        )

    def asless_comparison(self, args):
        return Tree("comparison", args)

    def asless_and_test(self, args):
        return Tree("and_test", args)

    def asless_or_test(self, args):
        return Tree("or_test", args)

    def asless_bitw_or(self, args):
        return Tree("bitw_or", args)

    def asless_bitw_xor(self, args):
        return Tree("bitw_xor", args)

    def asless_bitw_and(self, args):
        return Tree("bitw_and", args)

    def asless_shift_expr(self, args):
        return Tree("shift_expr", args)

    def asless_type_test(self, args):
        return Tree("type_test", args)

    def asless_content_test(self, args):
        return Tree("content_test", args)

    def asless_test_expr(self, args):
        return Tree("test_expr", args)

    def asless_arith_expr(self, args):
        return Tree("arith_expr", args)

    def asless_mdr_expr(self, args):
        return Tree("mdr_expr", args)

    def asless_pow_expr(self, args):
        return Tree("pow_expr", args)

    def string(self, args):
        string_token = args[0]
        return expression_to_str(string_token)

    def rstring(self, args):
        string_token = args[0]
        return expression_to_str(string_token)

    def par_pattern(self, args):
        return args[0] if len(args) > 0 else args

    def signal_stmt(self, args):
        if len(args) > 1 and len(args[1].children) == 0:
            return Tree("signal_stmt", args[:-1])
        return Tree("signal_stmt", args)

    def start(self, args):
        return Tree(
            "start",
            [
                arg
                for arg in args
                if not isinstance(arg, Tree)
                or arg.data not in ["annotation", "property_body_def"]
            ],
        )

    def class_def(self, args):
        return Tree(
            "class_def",
            [
                arg
                for arg in args
                if not isinstance(arg, Tree)
                or arg.data not in ["annotation", "property_body_def"]
            ],
        )

    def inline_property_body(self, _):
        return Tree("inline_property_body", [])


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
    spaces_for_indent: Optional[int] = None,
) -> None:
    code_formatted_again = format_code(
        formatted_code,
        max_line_length,
        parse_tree=parse_tree,
        comment_parse_tree=comment_parse_tree,
        spaces_for_indent=spaces_for_indent,
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
