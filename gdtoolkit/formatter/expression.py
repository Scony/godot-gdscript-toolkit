from functools import partial
from typing import Dict, Callable, List

from lark import Tree

from .context import Context, ExpressionContext
from .types import Node, Outcome, FormattedLines
from .expression_utils import (
    remove_outer_parentheses,
    is_foldable,
    is_expression_forcing_multiple_lines,
    is_any_comma,
    is_trailing_comma,
    has_leading_dot,
)
from .expression_to_str import expression_to_str


def format_expression(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    concrete_expression = remove_outer_parentheses(concrete_expression)
    return (
        _format_concrete_expression(concrete_expression, expression_context, context)[
            0
        ],  # TODO: make those to not return last processed line (at the very end)
        expression.end_line,
    )


# TOOD: refactor
# pylint: disable=too-many-locals
def format_comma_separated_list(
    a_list: List[Node], expression_context: ExpressionContext, context: Context
) -> FormattedLines:
    elements = [node for node in a_list if not is_any_comma(node)]
    fake_expression = Tree("fake", a_list)
    multiline_mode_forced = is_expression_forcing_multiple_lines(fake_expression)
    if not multiline_mode_forced:
        strings_to_join = map(expression_to_str, elements)
        single_line_expression = "{}{}{}".format(
            expression_context.prefix_string,
            ", ".join(strings_to_join),
            expression_context.suffix_string,
        )
        single_line_length = len(single_line_expression) + context.indent
        if single_line_length <= context.max_line_length:
            return [
                (
                    expression_context.prefix_line,
                    "{}{}".format(context.indent_string, single_line_expression),
                )
            ]
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    trailing_comma_present = is_trailing_comma(a_list[-1])
    child_context = context.create_child_context(expression_context.prefix_line)
    for i, element in enumerate(elements):
        suffix = (
            "," if i != len(elements) - 1 else ("," if trailing_comma_present else "")
        )
        child_expression_context = ExpressionContext("", element.line, suffix)
        lines, _ = _format_concrete_expression(
            element, child_expression_context, child_context
        )
        formatted_lines += lines
    formatted_lines.append(
        (
            a_list[-1].line,
            "{}{}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return formatted_lines


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
                    expression_to_str(expression),
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
    single_line_expression = expression_to_str(expression)
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
            expression_to_str(expression),
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
    handlers = {
        "assnmnt_expr": _format_assignment_expression_to_multiline_line,
        "test_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "or_test": _format_operator_chain_based_expression_to_multiple_lines,
        "and_test": _format_operator_chain_based_expression_to_multiple_lines,
        "not_test": partial(_append_to_expression_context_and_pass, " "),
        "content_test": _format_operator_chain_based_expression_to_multiple_lines,
        "comparison": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_or": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_xor": _format_operator_chain_based_expression_to_multiple_lines,
        "bitw_and": _format_operator_chain_based_expression_to_multiple_lines,
        "shift_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "subtr_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "addn_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "mdr_expr": _format_operator_chain_based_expression_to_multiple_lines,
        "neg_expr": partial(_append_to_expression_context_and_pass, ""),
        "bitw_not": partial(_append_to_expression_context_and_pass, ""),
        "type_test": _format_operator_chain_based_expression_to_multiple_lines,
        "type_cast": _format_operator_chain_based_expression_to_multiple_lines,
        "standalone_call": _format_call_expression_to_multiline_line,
        "getattr_call": _format_call_expression_to_multiline_line,
        "par_expr": _format_parentheses_to_multiple_lines,
        "array": _format_array_to_multiple_lines,
        "string": _format_string_to_multiple_lines,
        "dict": _format_dict_to_multiple_lines,
        "kv_pair": _format_kv_pair_to_multiple_lines,
        # fake expressions:
        "func_arg_regular": _format_func_arg_to_multiple_lines,
        "func_arg_inf": _format_func_arg_to_multiple_lines,
        "func_arg_typed": _format_func_arg_to_multiple_lines,
    }  # type: Dict[str, Callable]
    return handlers[expression.data](expression, expression_context, context)


def _format_array_to_multiple_lines(
    array: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    new_expression_context = ExpressionContext(
        "{}[".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "]{}".format(expression_context.suffix_string),
    )
    return (
        format_comma_separated_list(array.children, new_expression_context, context),
        array.end_line,
    )


def _format_dict_to_multiple_lines(
    a_dict: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    new_expression_context = ExpressionContext(
        "{}{{".format(expression_context.prefix_string),
        expression_context.prefix_line,
        "}}{}".format(expression_context.suffix_string),
    )
    return (
        format_comma_separated_list(a_dict.children, new_expression_context, context),
        a_dict.end_line,
    )


def _format_kv_pair_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    concrete_expression = expression.children[0]
    infix = ": " if concrete_expression.data == "c_dict_element" else " = "
    key_expression_context = ExpressionContext(
        expression_context.prefix_string, expression_context.prefix_line, ""
    )
    key_lines, _ = _format_concrete_expression(
        concrete_expression.children[0], key_expression_context, context
    )
    last_key_line_no, last_key_line = key_lines[-1]
    value_expression_context = ExpressionContext(
        "{}{}".format(last_key_line.strip(), infix),
        last_key_line_no,  # type: ignore
        expression_context.suffix_string,
    )
    value_lines, last_processed_line_no = _format_concrete_expression(
        concrete_expression.children[1], value_expression_context, context
    )
    return (key_lines[:-1] + value_lines, last_processed_line_no)


def _format_parentheses_to_multiple_lines(
    par_expr: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    child_expr = par_expr.children[0]
    if isinstance(child_expr, Tree) and child_expr.data == "par_expr":
        return _format_parentheses_to_multiple_lines(
            child_expr, expression_context, context
        )  # TODO: rethink that hack
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}(".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    child_context = context.create_child_context(expression_context.prefix_line)
    lines, _ = _format_concrete_expression(
        par_expr.children[0],
        ExpressionContext("", par_expr.children[0].line, ""),
        child_context,
    )
    formatted_lines += lines
    formatted_lines.append(
        (
            par_expr.children[-1].line,
            "{}){}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return (formatted_lines, par_expr.children[-1].line)


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


def _format_assignment_expression_to_multiline_line(
    expression: Tree, expression_context: ExpressionContext, context: Context,
) -> Outcome:
    new_expression_context = ExpressionContext(
        "{}{} = ".format(
            expression_context.prefix_string, expression_to_str(expression.children[0])
        ),
        expression_context.prefix_line,
        expression_context.suffix_string,
    )
    return _format_concrete_expression(
        expression.children[2], new_expression_context, context
    )


def _format_func_arg_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context,
) -> Outcome:
    if expression.data == "func_arg_regular" and len(expression.children) == 1:
        return _format_concrete_expression(
            expression.children[0], expression_context, context
        )
    if expression.data == "func_arg_typed" and len(expression.children) == 2:
        return (
            [
                (
                    expression.children[1].line,
                    "{}{}".format(context.indent_string, expression_to_str(expression)),
                )
            ],
            expression.children[1].line,
        )
    template = {
        "func_arg_regular": "{} = ",
        "func_arg_inf": "{} := ",
        "func_arg_typed": "{{}}: {} = ".format(expression.children[1]),
    }[expression.data]
    new_expression_context = ExpressionContext(
        template.format(expression.children[0].value),
        expression_context.prefix_line,
        expression_context.suffix_string,
    )
    return format_expression(expression.children[-1], new_expression_context, context)


def _format_call_expression_to_multiline_line(
    expression: Tree, expression_context: ExpressionContext, context: Context,
) -> Outcome:
    dot = "." if has_leading_dot(expression) else ""
    offset = 1 if has_leading_dot(expression) else 0
    callee = expression_to_str(expression.children[0 + offset])
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}{}{}(".format(
                context.indent_string, expression_context.prefix_string, dot, callee
            ),
        )
    ]  # type: FormattedLines
    elements = expression.children[2 + offset :: 2]
    child_context = context.create_child_context(expression_context.prefix_line)
    for i, element in enumerate(elements):
        suffix = "," if i != len(elements) - 1 else ""
        child_expression_context = ExpressionContext("", element.line, suffix)
        lines, _ = _format_concrete_expression(
            element, child_expression_context, child_context
        )
        formatted_lines += lines
    formatted_lines.append(
        (
            expression.children[-1].line,
            "{}){}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return (formatted_lines, expression.children[-1].line)


def _format_operator_chain_based_expression_to_multiple_lines(
    expression: Tree, expression_context: ExpressionContext, context: Context
) -> Outcome:
    formatted_lines = [
        (
            expression_context.prefix_line,
            "{}{}(".format(context.indent_string, expression_context.prefix_string),
        )
    ]  # type: FormattedLines
    child_context = context.create_child_context(expression_context.prefix_line)
    value = expression.children[0]
    lines, _ = _format_concrete_expression(
        value, ExpressionContext("", value.line, ""), child_context
    )
    formatted_lines += lines
    operator_expr_chain = zip(expression.children[1::2], expression.children[2::2])
    for operator, child in operator_expr_chain:
        lines, _ = _format_concrete_expression(
            child,
            ExpressionContext("{} ".format(operator.value), child.line, ""),
            child_context,
        )
        formatted_lines += lines
    formatted_lines.append(
        (
            expression.children[-1].line,
            "{}){}".format(context.indent_string, expression_context.suffix_string),
        )
    )
    return (formatted_lines, expression.children[-1].line)


def _append_to_expression_context_and_pass(
    spacing: str,
    expression: Tree,
    expression_context: ExpressionContext,
    context: Context,
) -> Outcome:
    str_to_append = expression_to_str(expression.children[0])
    new_expression_context = ExpressionContext(
        "{}{}{}".format(expression_context.prefix_string, str_to_append, spacing),
        expression_context.prefix_line,
        expression_context.suffix_string,
    )
    return _format_concrete_expression(
        expression.children[1], new_expression_context, context
    )
