from typing import List, Optional

from lark import Tree, Token

from ..common.utils import get_line, get_end_line
from ..common.types import Node


def remove_outer_parentheses(expression: Node) -> Node:
    if isinstance(expression, Tree) and expression.data == "par_expr":
        return remove_outer_parentheses(expression.children[0])
    return expression


def is_foldable(expression: Node) -> bool:
    if _is_multiline_string(expression):
        return True
    return not isinstance(expression, Token) and expression.data not in [
        "string",
        "rstring",
        "get_node",
        "node_path",
        "string_name",
        "unique_node_path",
        "signal_arg_typed",
        "signal_arg_regular",
        "non_foldable_dot_chain",
        "var_capture_pattern",
        "etc_pattern",
        "wildcard_pattern",
    ]


def has_trailing_comma(expression: Node) -> bool:
    return (
        isinstance(expression, Tree)
        and len(expression.children) > 0
        and isinstance(expression.children[-1], Tree)
        and expression.children[-1].data == "trailing_comma"
    )


def is_trailing_comma(expression: Node) -> bool:
    return isinstance(expression, Tree) and expression.data == "trailing_comma"


def is_expression_forcing_multiple_lines(
    expression: Node, standalone_comments: List[Optional[str]]
) -> bool:
    if has_trailing_comma(expression) or _is_multiline_string(expression):
        return True
    if isinstance(expression, Token):
        return False
    if (
        _has_standalone_comments(expression, standalone_comments)
        or _is_multistatement_lambda(expression)
        or _is_unistatement_lambda_with_compoud_statement(expression)
    ):
        return True
    for child in expression.children:
        if is_expression_forcing_multiple_lines(child, standalone_comments):
            return True
    return False


def expression_contains_lambda(expression: Node):
    if isinstance(expression, Token):
        return False
    if expression.data == "lambda":
        return True
    for child in expression.children:
        if expression_contains_lambda(child):
            return True
    return False


def is_any_comma(expression: Node) -> bool:
    return (isinstance(expression, Tree) and expression.data == "trailing_comma") or (
        isinstance(expression, Token) and expression.type == "COMMA"
    )


def is_any_parentheses(expression: Node) -> bool:
    return isinstance(expression, Token) and expression.type in ["LPAR", "RPAR"]


def _is_multiline_string(expression: Node) -> bool:
    return (
        isinstance(expression, Tree)
        and expression.data == "string"
        and expression.children[0].type == "LONG_STRING"
        and len(expression.children[0].value.splitlines()) > 1
    )


def _has_standalone_comments(
    expression: Tree, standalone_comments: List[Optional[str]]
) -> bool:
    return any(
        comment is not None
        for comment in standalone_comments[
            get_line(expression) : get_end_line(expression)
        ]
    )


def _is_multistatement_lambda(expression: Tree) -> bool:
    return (
        isinstance(expression, Tree)
        and expression.data == "lambda"
        and len(expression.children) > 2
    )


# TODO: remove once such statements are supported
def _is_unistatement_lambda_with_compoud_statement(expression: Tree) -> bool:
    return (
        isinstance(expression, Tree)
        and expression.data == "lambda"
        and len(expression.children) == 2
        and isinstance(expression.children[1], Tree)
        and expression.children[1].data
        in ["if_stmt", "while_stmt", "for_stmt", "for_stmt_typed", "match_stmt"]
    )
