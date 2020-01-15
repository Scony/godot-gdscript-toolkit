from lark import Tree, Token

from .context import Context
from .types import Prefix, Node, Outcome, FormattedLines


def format_expression(prefix: Prefix, expression: Tree, context: Context) -> Outcome:
    concrete_expression = expression.children[0]
    concrete_expression = _remove_outer_parentheses(concrete_expression)
    return _format_concrete_expression(prefix, concrete_expression, context)


def _remove_outer_parentheses(expression: Node) -> Node:
    if isinstance(expression, Tree) and expression.data == "par_expr":
        return _remove_outer_parentheses(expression.children[0])
    return expression


def _format_concrete_expression(
    prefix: Prefix, expression: Node, context: Context
) -> Outcome:
    assert context
    formatted_lines = []  # type: FormattedLines
    if not _is_foldable(expression):
        formatted_lines.append(
            (
                prefix.line,
                "{}{}{}".format(
                    context.indent_string,
                    prefix.string,
                    _format_non_foldable(expression),
                ),
            )
        )
    return (formatted_lines, expression.line)


def _is_foldable(expression: Node) -> bool:
    return not isinstance(expression, Token) and expression.data not in [
        "string",
        "node_path",
        "get_node",
    ]


def _format_non_foldable(expression: Node) -> str:
    if isinstance(expression, Tree):
        if expression.data == "string":
            return expression.children[0].value
        if expression.data == "node_path":
            return "{}{}".format("@", _format_non_foldable(expression.children[0]))
        if expression.data == "get_node":
            return "{}{}".format("$", _format_non_foldable(expression.children[0]))
        if expression.data == "path":
            return "/".join([name_token.value for name_token in expression.children])
    return expression.value
