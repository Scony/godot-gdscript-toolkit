from lark import Tree, Token

from .types import Node


def remove_outer_parentheses(expression: Node) -> Node:
    if isinstance(expression, Tree) and expression.data == "par_expr":
        return remove_outer_parentheses(expression.children[0])
    return expression


def is_foldable(expression: Node) -> bool:
    if _is_multiline_string(expression):
        return True
    return not isinstance(expression, Token) and expression.data not in [
        "string",
        "node_path",
        "get_node",
    ]


def _is_multiline_string(expression: Node) -> bool:
    return (
        isinstance(expression, Tree)
        and expression.data == "string"
        and expression.children[0].type == "LONG_STRING"
        and len(expression.children[0].value.splitlines()) > 1
    )


def has_trailing_comma(expression: Node) -> bool:
    return (
        isinstance(expression, Tree)
        and len(expression.children) > 0
        and isinstance(expression.children[-1], Tree)
        and expression.children[-1].data == "trailing_comma"
    )


def is_trailing_comma(expression: Node) -> bool:
    return isinstance(expression, Tree) and expression.data == "trailing_comma"


def is_expression_forcing_multiple_lines(expression: Node) -> bool:
    if has_trailing_comma(expression):
        return True
    if _is_multiline_string(expression):
        return True
    if isinstance(expression, Token):
        return False
    for child in expression.children:
        if is_expression_forcing_multiple_lines(child):
            return True
    return False


def is_any_comma(expression: Node) -> bool:
    return (isinstance(expression, Tree) and expression.data == "trailing_comma") or (
        isinstance(expression, Token) and expression.type == "COMMA"
    )


def is_any_parentheses(expression: Node) -> bool:
    return isinstance(expression, Token) and expression.type in ["LPAR", "RPAR"]


def has_leading_dot(expression: Node) -> bool:
    return (
        isinstance(expression.children[0], Token)
        and expression.children[0].type == "DOT"
    )
