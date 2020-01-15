from lark import Tree, Token

from .context import Context
from .types import Prefix, Node, Outcome


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
    if _is_foldable(expression):
        return _format_foldable(prefix, expression, context)
    return (
        [
            (
                prefix.line,
                "{}{}{}".format(
                    context.indent_string,
                    prefix.string,
                    _non_foldable_to_str(expression),
                ),
            )
        ],
        prefix.line,
    )


def _is_foldable(expression: Node) -> bool:
    return not isinstance(expression, Token) and expression.data not in [
        "string",
        "node_path",
        "get_node",
    ]


def _format_foldable(prefix: Prefix, expression: Node, context: Context) -> Outcome:
    single_line = "{}{}{}".format(
        context.indent_string, prefix.string, _foldable_to_str(expression),
    )
    return ([(prefix.line, single_line)], prefix.line)


def _expression_to_str(expression: Node) -> str:
    if _is_foldable(expression):
        return _foldable_to_str(expression)
    return _non_foldable_to_str(expression)


def _foldable_to_str(expression: Node) -> str:
    if expression.data == "array":
        array_elements = [
            _expression_to_str(child)
            for child in expression.children
            if isinstance(child, Tree) or child.type != "COMMA"
        ]
        return "[{}]".format(", ".join(array_elements))
    return ""


def _non_foldable_to_str(expression: Node) -> str:
    if isinstance(expression, Tree):
        if expression.data == "string":
            return expression.children[0].value
        if expression.data == "node_path":
            return "{}{}".format("@", _non_foldable_to_str(expression.children[0]))
        if expression.data == "get_node":
            return "{}{}".format("$", _non_foldable_to_str(expression.children[0]))
        if expression.data == "path":
            return "/".join([name_token.value for name_token in expression.children])
    return expression.value
