from lark import Tree

from .context import Context, ExpressionContext
from .types import Node, Outcome, FormattedLines
from .expression_utils import (
    remove_outer_parentheses,
    is_foldable,
    is_expression_forcing_multiple_lines,
    is_any_comma,
    has_trailing_comma,
)
from .expression_to_str import (
    expression_to_str,
    foldable_to_str,
    non_foldable_to_str,
)


def format_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    concrete_expression = remove_outer_parentheses(concrete_expression)
    return _format_concrete_expression(concrete_expression, expression_context, context)


def _format_concrete_expression(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if is_foldable(expression):
        return _format_foldable(expression, expression_context, context)
    return (
        [
            (
                expression_context.prefix_line,
                "{}{}{}{}".format(
                    context.indent_string,
                    expression_context.prefix_string,
                    non_foldable_to_str(expression),
                    expression_context.suffix_string,
                ),
            )
        ],
        expression_context.prefix_line,
    )


def _format_foldable(
    expression: Node, expression_context: ExpressionContext, context: Context
) -> Outcome:
    if is_expression_forcing_multiple_lines(expression):
        return _format_foldable_to_multiple_lines(
            expression, expression_context, context
        )
    single_line_expression = foldable_to_str(expression)
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
            foldable_to_str(expression),
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
    if expression.data == "dict":
        return _format_dict_to_multiple_lines(expression, expression_context, context)
    if expression.data == "string":
        return _format_string_to_multiple_lines(expression, expression_context, context)
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
    array_elements = [child for child in array.children if not is_any_comma(child)]
    child_context = context.create_child_context(expression_context.prefix_line)
    for i, element in enumerate(array_elements):
        suffix = (
            ","
            if i != len(array_elements) - 1
            else ("," if has_trailing_comma(array) else "")
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
    elements = [child for child in a_dict.children if not is_any_comma(child)]
    for i, element in enumerate(elements):
        key = element.children[0]
        value = element.children[1]
        is_last_element = i == len(elements) - 1
        infix = ": " if element.data == "c_dict_element" else " = "
        single_line_expression = "{}{}{}".format(
            expression_to_str(key), infix, expression_to_str(value),
        )
        comma = 0 if is_last_element and not has_trailing_comma(a_dict) else 1
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


def _format_string_to_multiple_lines(
    string: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    long_string = string.children[0]
    lines = long_string.value.splitlines()
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}{}".format(
                context.indent_string, expression_context.prefix_string, lines[0]
            ),
        )
    ]  # type: FormattedLines
    for middle_line in lines[1:-1]:
        formatted_lines.append((string.line, middle_line))
    formatted_lines.append(
        (string.line, "{}{}".format(lines[-1], expression_context.suffix_string))
    )
    return (formatted_lines, string.line)
