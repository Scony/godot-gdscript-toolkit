from lark import Tree, Token

from .context import Context, ExpressionContext
from .types import Node, Outcome, FormattedLines


def format_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    concrete_expression = _remove_outer_parentheses(concrete_expression)
    return _format_concrete_expression(concrete_expression, expression_context, context)


def _remove_outer_parentheses(expression: Node) -> Node:
    if isinstance(expression, Tree) and expression.data == "par_expr":
        return _remove_outer_parentheses(expression.children[0])
    return expression


def _format_concrete_expression(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if _is_foldable(expression):
        return _format_foldable(expression, expression_context, context)
    return (
        [
            (
                expression_context.prefix_line,
                "{}{}{}{}".format(
                    context.indent_string,
                    expression_context.prefix_string,
                    _non_foldable_to_str(expression),
                    expression_context.suffix_string,
                ),
            )
        ],
        expression_context.prefix_line,
    )


def _is_foldable(expression: Node) -> bool:
    return not isinstance(expression, Token) and expression.data not in [
        "string",
        "node_path",
        "get_node",
    ]


def _format_foldable(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    single_line_expression = _foldable_to_str(expression)
    single_line_length = (
        context.indent
        + len(expression_context.prefix_string)
        + len(single_line_expression)
        + len(expression_context.suffix_string)
    )
    if single_line_length <= context.max_line_length:
        single_line = "{}{}{}{}".format(
            context.indent_string,
            expression_context.prefix_string,
            _foldable_to_str(expression),
            expression_context.suffix_string,
        )
        return (
            [(expression_context.prefix_line, single_line)],
            expression_context.prefix_line,
        )
    return _format_foldable_to_multiple_lines(expression, expression_context, context)


def _format_foldable_to_multiple_lines(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if expression.data != "array":
        raise NotImplementedError
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}[".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    array_elements = [
        child
        for child in expression.children
        if isinstance(child, Tree) or child.type != "COMMA"
    ]
    child_context = context.create_child_context(expression_context.prefix_line)
    for i, element in enumerate(array_elements):
        suffix = "," if i != len(array_elements) - 1 else ""
        child_expression_context = ExpressionContext("", element.line, suffix)
        lines, _ = _format_concrete_expression(
            element, child_expression_context, child_context
        )
        formatted_lines += lines
    formatted_lines.append(
        (
            expression.children[-1].line,
            "{}]{}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return (formatted_lines, expression.children[-1].line)


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
