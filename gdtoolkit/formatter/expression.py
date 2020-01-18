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
    if _is_expression_forcing_multiple_lines(expression):
        return _format_foldable_to_multiple_lines(
            expression, expression_context, context
        )
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


def _is_expression_forcing_multiple_lines(expression: Node) -> bool:
    if _has_trailing_comma(expression):
        return True
    for child in expression.children:
        if _has_trailing_comma(child):
            return True
    return False


def _has_trailing_comma(expression: Node) -> bool:
    return (
        isinstance(expression, Tree)
        and len(expression.children) > 0
        and isinstance(expression.children[-1], Tree)
        and expression.children[-1].data == "trailing_comma"
    )


def _format_foldable_to_multiple_lines(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if expression.data == "dict":
        return _format_dict_to_multiple_lines(expression, expression_context, context)
    assert expression.data == "array"
    return _format_array_to_multiple_lines(expression, expression_context, context)


def _format_array_to_multiple_lines(
    array: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}[".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    array_elements = [child for child in array.children if not _is_any_comma(child)]
    child_context = context.create_child_context(expression_context.prefix_line)
    for i, element in enumerate(array_elements):
        suffix = (
            ","
            if i != len(array_elements) - 1
            else ("," if _has_trailing_comma(array) else "")
        )
        child_expression_context = ExpressionContext("", element.line, suffix)
        lines, _ = _format_concrete_expression(
            element, child_expression_context, child_context
        )
        formatted_lines += lines
    formatted_lines.append(
        (
            array.children[-1].line,
            "{}]{}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return (formatted_lines, array.children[-1].line)


# TOOD: refactor
# pylint: disable=too-many-locals
def _format_dict_to_multiple_lines(
    a_dict: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}{{".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    child_context = context.create_child_context(expression_context.prefix_line)
    elements = [child for child in a_dict.children if not _is_any_comma(child)]
    for i, element in enumerate(elements):
        key = element.children[0]
        value = element.children[1]
        is_last_element = i == len(elements) - 1
        infix = ": " if element.data == "c_dict_element" else " = "
        single_line_expression = "{}{}{}".format(
            _expression_to_str(key), infix, _expression_to_str(value),
        )
        comma = 0 if is_last_element and not _has_trailing_comma(a_dict) else 1
        single_line_length = len(single_line_expression) + child_context.indent + comma
        if single_line_length <= context.max_line_length:
            suffix = "," * comma
            single_line = "{}{}{}".format(
                child_context.indent_string, single_line_expression, suffix
            )
            formatted_lines.append((element.line, single_line))
        else:
            key_expression_context = ExpressionContext("", key.line, infix[:-1])
            key_lines, _ = _format_concrete_expression(
                key, key_expression_context, child_context
            )
            formatted_lines += key_lines
            value_expression_context = ExpressionContext("", value.line, "," * comma)
            value_lines, _ = _format_concrete_expression(
                value, value_expression_context, child_context
            )
            formatted_lines += value_lines

    formatted_lines.append(
        (
            a_dict.children[-1].line,
            "{}}}{}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return (formatted_lines, a_dict.children[-1].line)


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
    if expression.data == "dict":
        elements = [_dict_element_to_str(child) for child in expression.children]
        return "{{{}}}".format(", ".join(elements))
    return ""


def _dict_element_to_str(dict_element: Tree) -> str:
    template = "{}: {}" if dict_element.data == "c_dict_element" else "{} = {}"
    return template.format(
        _expression_to_str(dict_element.children[0]),
        _expression_to_str(dict_element.children[1]),
    )


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


def _is_any_comma(expression: Node) -> bool:
    return (isinstance(expression, Tree) and expression.data == "trailing_comma") or (
        isinstance(expression, Token) and expression.type == "COMMA"
    )
